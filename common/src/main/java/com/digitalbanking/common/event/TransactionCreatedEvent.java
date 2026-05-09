package com.digitalbanking.common.event;

import com.fasterxml.jackson.annotation.JsonProperty;
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

    @JsonProperty("transaction_id")
    private UUID transactionId;

    @JsonProperty("from_account_id")
    private UUID fromAccountId;

    @JsonProperty("to_account_id")
    private UUID toAccountId;

    /**
     * Transaction type: DEPOSIT, WITHDRAWAL, or TRANSFER.
     * Serialized as "transaction_type" to match the Python Notification Service schema.
     * Internal Java code (including LedgerService @EventListener) continues to call getType().
     */
    @JsonProperty("transaction_type")
    private String type;

    @JsonProperty("amount")
    private BigDecimal amount;

    @JsonProperty("description")
    private String description;

    @JsonProperty("timestamp")
    private long timestamp;

    // Notification Service fields (MVP placeholders — real values require account-service lookup)
    @JsonProperty("recipient_email")
    private String recipientEmail;

    @JsonProperty("customer_name")
    private String customerName;

    @JsonProperty("account_number")
    private String accountNumber;

    public TransactionCreatedEvent(Object source) {
        this.timestamp = System.currentTimeMillis();
    }
}
