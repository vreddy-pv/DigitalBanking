package com.digitalbanking.ledger.event;

import com.digitalbanking.common.event.TransactionCreatedEvent;
import com.digitalbanking.ledger.service.LedgerService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class TransactionEventListener {

    private final LedgerService ledgerService;

    @EventListener
    public void handleTransactionCreatedEvent(TransactionCreatedEvent event) {
        try {
            log.info("Processing transaction event: {}", event.getTransactionId());

            ledgerService.createJournalEntries(
                    event.getTransactionId(),
                    event.getType(),
                    event.getAmount(),
                    event.getFromAccountId(),
                    event.getToAccountId()
            );

            log.info("Journal entries created successfully for transaction: {}", event.getTransactionId());
        } catch (Exception ex) {
            log.error("Error processing transaction event: {}", event.getTransactionId(), ex);
            throw ex;
        }
    }
}
