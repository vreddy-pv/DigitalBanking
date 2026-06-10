package com.digitalbanking.ops.service;

import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.ops.dto.*;
import com.digitalbanking.ops.entity.OpsCase;
import com.digitalbanking.ops.repository.OpsCaseRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class OpsCaseService {

    private final OpsCaseRepository repository;
    private final ComplaintServiceClient complaintClient;

    // ── Event-driven creation ─────────────────────────────────────────────────

    @Transactional
    public void createCase(Map<String, Object> event) {
        String ticketId = (String) event.get("ticketId");
        if (ticketId == null || repository.existsByTicketId(ticketId)) {
            log.warn("Skipping duplicate or invalid complaint.created event for ticketId={}", ticketId);
            return;
        }

        OpsCase opsCase = new OpsCase();
        opsCase.setTicketId(ticketId);
        opsCase.setUserId(String.valueOf(event.getOrDefault("userId", "")));
        opsCase.setAccountId((String) event.get("accountId"));
        opsCase.setTransactionId((String) event.get("transactionId"));
        opsCase.setProductLine((String) event.get("productLine"));
        opsCase.setComplaintType((String) event.get("complaintType"));

        Object sla = event.get("slaDeadlineHours");
        if (sla instanceof Number n) opsCase.setSlaDeadlineHours(n.intValue());

        repository.save(opsCase);
        log.info("OpsCase created for ticketId={}", ticketId);
    }

    @Transactional
    public void updateWithInvestigation(Map<String, Object> event) {
        String ticketId = (String) event.get("ticketId");
        OpsCase opsCase = repository.findByTicketId(ticketId).orElse(null);
        if (opsCase == null) {
            log.warn("Received complaint.investigated for unknown ticketId={} — skipping", ticketId);
            return;
        }

        Object scoreObj = event.get("riskScore");
        if (scoreObj instanceof Number n) opsCase.setRiskScore(n.intValue());
        opsCase.setRiskLevel((String) event.get("riskLevel"));
        opsCase.setInvestigationSummary((String) event.get("summary"));
        opsCase.setRecommendedAction((String) event.get("recommendedAction"));

        Object flagsObj = event.get("flags");
        if (flagsObj != null) opsCase.setFlags(flagsObj.toString());

        String action = (String) event.get("recommendedAction");
        if ("AUTO_RESOLVE".equals(action)) {
            opsCase.setCaseStatus(OpsCase.CaseStatus.RESOLVED);
            opsCase.setOutcome("RESOLVED");
        } else if ("ESCALATE_FRAUD".equals(action)) {
            opsCase.setCaseStatus(OpsCase.CaseStatus.ESCALATED);
            opsCase.setOutcome("ESCALATED");
        } else {
            opsCase.setCaseStatus(OpsCase.CaseStatus.AWAITING_REVIEW);
        }

        repository.save(opsCase);
        log.info("OpsCase updated with investigation for ticketId={} status={}", ticketId, opsCase.getCaseStatus());
    }

    // ── Read operations ───────────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public List<CaseResponse> listCases(String status, String assignedTo) {
        if (status != null && assignedTo != null) {
            OpsCase.CaseStatus cs = parseCaseStatus(status);
            return repository.findByCaseStatusAndAssignedToOrderByReceivedAtDesc(cs, assignedTo)
                    .stream().map(CaseResponse::from).collect(Collectors.toList());
        }
        if (status != null) {
            return repository.findByCaseStatusOrderByReceivedAtDesc(parseCaseStatus(status))
                    .stream().map(CaseResponse::from).collect(Collectors.toList());
        }
        if (assignedTo != null) {
            return repository.findByAssignedToOrderByReceivedAtDesc(assignedTo)
                    .stream().map(CaseResponse::from).collect(Collectors.toList());
        }
        return repository.findAllByOrderByReceivedAtDesc()
                .stream().map(CaseResponse::from).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public CaseResponse getCase(String ticketId) {
        return CaseResponse.from(findCase(ticketId));
    }

    @Transactional(readOnly = true)
    public OpsStatsResponse getStats() {
        List<Object[]> rows = repository.countByCaseStatus();
        Map<String, Long> counts = new HashMap<>();
        for (Object[] row : rows) {
            counts.put(row[0].toString(), (Long) row[1]);
        }
        long open = counts.getOrDefault("OPEN", 0L);
        long investigating = counts.getOrDefault("UNDER_INVESTIGATION", 0L);
        long awaiting = counts.getOrDefault("AWAITING_REVIEW", 0L);
        return OpsStatsResponse.builder()
                .open(open)
                .underInvestigation(investigating)
                .awaitingReview(awaiting)
                .resolved(counts.getOrDefault("RESOLVED", 0L))
                .escalated(counts.getOrDefault("ESCALATED", 0L))
                .rejected(counts.getOrDefault("REJECTED", 0L))
                .totalActive(open + investigating + awaiting)
                .build();
    }

    // ── Write operations ──────────────────────────────────────────────────────

    @Transactional
    public CaseResponse assignCase(String ticketId, AssignCaseRequest request) {
        OpsCase opsCase = findCase(ticketId);
        if (opsCase.getCaseStatus() == OpsCase.CaseStatus.RESOLVED
                || opsCase.getCaseStatus() == OpsCase.CaseStatus.REJECTED
                || opsCase.getCaseStatus() == OpsCase.CaseStatus.ESCALATED) {
            throw new AppException("CASE_ALREADY_CLOSED",
                    "Case " + ticketId + " is already " + opsCase.getCaseStatus());
        }
        opsCase.setAssignedTo(request.getAnalystId());
        if (opsCase.getCaseStatus() == OpsCase.CaseStatus.OPEN) {
            opsCase.setCaseStatus(OpsCase.CaseStatus.AWAITING_REVIEW);
        }
        return CaseResponse.from(repository.save(opsCase));
    }

    @Transactional
    public CaseResponse resolveCase(String ticketId, ResolveCaseRequest request) {
        OpsCase opsCase = findCase(ticketId);
        if (opsCase.getCaseStatus() == OpsCase.CaseStatus.RESOLVED
                || opsCase.getCaseStatus() == OpsCase.CaseStatus.REJECTED
                || opsCase.getCaseStatus() == OpsCase.CaseStatus.ESCALATED) {
            throw new AppException("CASE_ALREADY_CLOSED",
                    "Case " + ticketId + " is already " + opsCase.getCaseStatus());
        }

        OpsCase.CaseStatus newStatus = OpsCase.CaseStatus.valueOf(request.getOutcome());
        opsCase.setCaseStatus(newStatus);
        opsCase.setOutcome(request.getOutcome());
        if (request.getOpsNotes() != null) opsCase.setOpsNotes(request.getOpsNotes());

        // Mirror the resolution to complaint-service
        String complaintStatus = switch (request.getOutcome()) {
            case "RESOLVED" -> "RESOLVED";
            case "ESCALATED" -> "ESCALATED";
            default -> "REJECTED";
        };
        complaintClient.updateStatus(ticketId, complaintStatus, request.getOutcome(), request.getOpsNotes());

        return CaseResponse.from(repository.save(opsCase));
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private OpsCase findCase(String ticketId) {
        return repository.findByTicketId(ticketId)
                .orElseThrow(() -> new AppException("CASE_NOT_FOUND", "Case not found: " + ticketId));
    }

    private OpsCase.CaseStatus parseCaseStatus(String status) {
        try {
            return OpsCase.CaseStatus.valueOf(status.toUpperCase());
        } catch (IllegalArgumentException ex) {
            throw new AppException("INVALID_STATUS", "Unknown status: " + status);
        }
    }
}
