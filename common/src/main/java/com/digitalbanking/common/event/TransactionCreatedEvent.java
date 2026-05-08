package com.digitalbanking.common.event;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TransactionCreatedEvent {

    private UUID transactionId;

    private UUID fromAccountId;

    private UUID toAccountId;

    private String type;

    private BigDecimal amount;

    private String description;

    private long timestamp;

    public TransactionCreatedEvent(Object source) {
        this.timestamp = System.currentTimeMillis();
    }
}
