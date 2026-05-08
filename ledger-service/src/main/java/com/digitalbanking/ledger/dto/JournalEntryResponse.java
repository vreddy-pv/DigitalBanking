package com.digitalbanking.ledger.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import com.fasterxml.jackson.annotation.JsonInclude;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class JournalEntryResponse {

    private UUID id;

    private UUID transactionId;

    private UUID glAccountId;

    private BigDecimal debit;

    private BigDecimal credit;

    private LocalDateTime timestamp;
}
