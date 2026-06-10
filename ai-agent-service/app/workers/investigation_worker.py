"""
Investigation Worker — consumes complaint.created events from RabbitMQ,
runs a Claude-powered fraud analysis, updates complaint-service with findings,
then publishes a complaint.investigated event for the ops-service.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

import aio_pika
import anthropic
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "banking.events"
INVESTIGATION_QUEUE = "investigation_worker_queue"
CONSUME_ROUTING_KEY = "complaint.created"
PUBLISH_ROUTING_KEY = "complaint.investigated"

_INVESTIGATION_SYSTEM = """\
You are a financial fraud investigation system for a bank's digital platform.
Analyze the complaint and transaction data provided and return a risk assessment.
IMPORTANT: Respond with valid JSON only — no markdown, no backticks, no extra text.
"""

_FALLBACK_RESULT = {
    "risk_score": 50,
    "risk_level": "MEDIUM",
    "flags": [],
    "summary": "Automated investigation inconclusive — manual review required.",
    "recommended_action": "MANUAL_REVIEW",
    "key_findings": ["Insufficient transaction data for automated analysis."],
}


class InvestigationWorker:
    def __init__(self):
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._anthropic = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start(self) -> None:
        for attempt in range(1, 11):
            try:
                self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=5)

                exchange = await self._channel.declare_exchange(
                    EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
                )
                queue = await self._channel.declare_queue(
                    INVESTIGATION_QUEUE, durable=True
                )
                await queue.bind(exchange, routing_key=CONSUME_ROUTING_KEY)
                await queue.consume(self._handle_message)

                logger.info("InvestigationWorker connected to RabbitMQ and consuming %s", CONSUME_ROUTING_KEY)
                return
            except Exception as exc:
                wait = 2 ** attempt
                logger.warning("RabbitMQ connect attempt %d failed: %s — retrying in %ds", attempt, exc, wait)
                await asyncio.sleep(wait)

        logger.error("InvestigationWorker could not connect to RabbitMQ after 10 attempts — investigation disabled")

    async def stop(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("InvestigationWorker disconnected")

    # ── Message handler ───────────────────────────────────────────────────────

    async def _handle_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                event = json.loads(message.body.decode())
                logger.info("InvestigationWorker received complaint.created: ticketId=%s", event.get("ticketId"))
                await self._investigate(event)
            except Exception as exc:
                logger.error("InvestigationWorker failed to process message: %s", exc, exc_info=True)

    async def _investigate(self, event: dict) -> None:
        ticket_id = event.get("ticketId", "UNKNOWN")
        transaction_id = event.get("transactionId")
        account_id = event.get("accountId")

        # 1 — Mark complaint as under investigation immediately
        await self._update_complaint(
            ticket_id,
            status="UNDER_INVESTIGATION",
            resolution="Automated investigation in progress.",
        )

        # 2 — Gather transaction context
        txn_detail, recent_txns = await self._fetch_transaction_context(transaction_id, account_id)

        # 3 — Run Claude analysis
        result = await self._run_claude_investigation(event, txn_detail, recent_txns)

        # 4 — Update complaint with findings
        final_status, outcome = _map_action_to_status(result["recommended_action"])
        await self._update_complaint(
            ticket_id,
            status=final_status,
            resolution=_format_resolution(result),
            outcome=outcome,
        )

        # 5 — Publish investigated event for ops-service
        await self._publish_investigated_event(ticket_id, event, result)

        logger.info(
            "Investigation complete: ticketId=%s riskLevel=%s action=%s",
            ticket_id, result["risk_level"], result["recommended_action"],
        )

    # ── Data fetching ─────────────────────────────────────────────────────────

    async def _fetch_transaction_context(
        self, transaction_id: str | None, account_id: str | None
    ) -> tuple[dict, list[dict]]:
        txn_detail: dict = {}
        recent_txns: list[dict] = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            if transaction_id:
                try:
                    resp = await client.get(
                        f"{settings.transaction_service_url}/api/v1/transactions/{transaction_id}"
                    )
                    if resp.status_code == 200:
                        txn_detail = resp.json().get("data", resp.json())
                except Exception as exc:
                    logger.warning("Could not fetch transaction %s: %s", transaction_id, exc)

            if account_id:
                try:
                    resp = await client.get(
                        f"{settings.transaction_service_url}/api/v1/transactions/account/{account_id}"
                    )
                    if resp.status_code == 200:
                        raw = resp.json()
                        recent_txns = raw if isinstance(raw, list) else raw.get("data", [])
                        recent_txns = recent_txns[:50]
                except Exception as exc:
                    logger.warning("Could not fetch recent transactions for account %s: %s", account_id, exc)

        return txn_detail, recent_txns

    # ── Claude analysis ───────────────────────────────────────────────────────

    async def _run_claude_investigation(
        self, event: dict, txn_detail: dict, recent_txns: list[dict]
    ) -> dict:
        prompt = _build_investigation_prompt(event, txn_detail, recent_txns)
        try:
            response = await self._anthropic.messages.create(
                model=settings.model,
                max_tokens=1024,
                system=_INVESTIGATION_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text.strip()
            result = json.loads(raw_text)
            # Validate required keys exist
            for key in ("risk_score", "risk_level", "flags", "summary", "recommended_action", "key_findings"):
                if key not in result:
                    raise ValueError(f"Missing key: {key}")
            return result
        except Exception as exc:
            logger.error("Claude investigation failed for ticketId=%s: %s", event.get("ticketId"), exc)
            return _FALLBACK_RESULT

    # ── Complaint update ──────────────────────────────────────────────────────

    async def _update_complaint(
        self, ticket_id: str, status: str, resolution: str, outcome: str | None = None
    ) -> None:
        payload: dict = {"status": status, "resolution": resolution}
        if outcome:
            payload["outcome"] = outcome
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.put(
                    f"{settings.complaint_service_url}/api/v1/complaints/{ticket_id}/status",
                    json=payload,
                )
                if resp.status_code not in (200, 204):
                    logger.warning("Unexpected response updating complaint %s: %d", ticket_id, resp.status_code)
        except Exception as exc:
            logger.error("Failed to update complaint %s: %s", ticket_id, exc)

    # ── Event publishing ──────────────────────────────────────────────────────

    async def _publish_investigated_event(
        self, ticket_id: str, original_event: dict, result: dict
    ) -> None:
        if not self._channel:
            return
        try:
            exchange = await self._channel.get_exchange(EXCHANGE_NAME)
            payload = {
                "eventType": "ComplaintInvestigatedEvent",
                "ticketId": ticket_id,
                "userId": original_event.get("userId"),
                "complaintType": original_event.get("complaintType"),
                "productLine": original_event.get("productLine"),
                "riskScore": result["risk_score"],
                "riskLevel": result["risk_level"],
                "flags": result["flags"],
                "summary": result["summary"],
                "recommendedAction": result["recommended_action"],
                "keyFindings": result.get("key_findings", []),
                "investigatedAt": datetime.now(timezone.utc).isoformat(),
            }
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=PUBLISH_ROUTING_KEY,
            )
            logger.info("Published complaint.investigated for ticketId=%s", ticket_id)
        except Exception as exc:
            logger.error("Failed to publish investigated event for %s: %s", ticket_id, exc)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _map_action_to_status(recommended_action: str) -> tuple[str, str | None]:
    """Map Claude's recommended action to complaint-service status + outcome."""
    if recommended_action == "AUTO_RESOLVE":
        return "RESOLVED", "RESOLVED"
    if recommended_action == "ESCALATE_FRAUD":
        return "ESCALATED", "ESCALATED"
    return "UNDER_INVESTIGATION", None  # MANUAL_REVIEW — ops picks up


def _format_resolution(result: dict) -> str:
    flags_str = ", ".join(result.get("flags", [])) or "none"
    findings = "\n".join(f"• {f}" for f in result.get("key_findings", []))
    return (
        f"[AUTO-INVESTIGATION] Risk: {result['risk_level']} ({result['risk_score']}/100)\n"
        f"Flags: {flags_str}\n"
        f"Summary: {result['summary']}\n"
        f"Findings:\n{findings}"
    )


def _build_investigation_prompt(event: dict, txn_detail: dict, recent_txns: list[dict]) -> str:
    complaint_type = event.get("complaintType", "UNKNOWN")
    product_line = event.get("productLine", "UNKNOWN")
    sla_hours = event.get("slaDeadlineHours", 48)
    ticket_id = event.get("ticketId", "UNKNOWN")

    # Velocity metrics
    amounts = [float(t.get("amount", 0)) for t in recent_txns if t.get("amount")]
    avg_amount = sum(amounts) / len(amounts) if amounts else 0
    disputed_amount = float(txn_detail.get("amount", 0))
    amount_ratio = round(disputed_amount / avg_amount, 1) if avg_amount > 0 else 0

    txn_summary = json.dumps(txn_detail, indent=2, default=str) if txn_detail else "Transaction details unavailable."
    recent_summary = (
        json.dumps(recent_txns[:10], indent=2, default=str) if recent_txns
        else "No recent transaction history available."
    )

    return f"""Investigate this banking complaint and return a risk assessment as JSON.

COMPLAINT:
- Ticket: {ticket_id}
- Type: {complaint_type} (UNAUTHORIZED=customer never made this | FRAUD=suspected fraud | DISPUTE=wrong amount | ERROR=system error)
- Product: {product_line}
- SLA: {sla_hours} hours

DISPUTED TRANSACTION:
{txn_summary}

RECENT ACCOUNT ACTIVITY (last {len(recent_txns)} transactions, showing first 10):
{recent_summary}

VELOCITY METRICS:
- Total recent transactions analysed: {len(recent_txns)}
- Average transaction amount: ₹{avg_amount:,.2f}
- Disputed amount vs average: {amount_ratio}x

Analyze for: unusual velocity, amount anomalies, merchant patterns, time-of-day patterns, known fraud patterns.
Consider the complaint type carefully — UNAUTHORIZED and FRAUD warrant stricter scrutiny.

Return this exact JSON (no markdown, no backticks):
{{
  "risk_score": <integer 0-100>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "flags": ["<FLAG>"],
  "summary": "<2-3 sentence investigation summary>",
  "recommended_action": "<AUTO_RESOLVE|MANUAL_REVIEW|ESCALATE_FRAUD>",
  "key_findings": ["<finding 1>", "<finding 2>"]
}}

Guidelines:
- risk_score: LOW=0-25, MEDIUM=26-50, HIGH=51-75, CRITICAL=76-100
- AUTO_RESOLVE: only when risk_score < 25 and complaint_type is ERROR or DISPUTE
- ESCALATE_FRAUD: when risk_score > 75 or complaint_type is FRAUD/UNAUTHORIZED with strong signals
- MANUAL_REVIEW: all other cases
- Possible flags: VELOCITY_ANOMALY, LARGE_AMOUNT, UNUSUAL_MERCHANT, OFF_HOURS, GEOGRAPHIC_ANOMALY, PATTERN_MATCH_FRAUD, HIGH_RISK_TYPE, INSUFFICIENT_DATA"""
