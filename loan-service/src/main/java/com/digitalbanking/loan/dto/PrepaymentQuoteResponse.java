package com.digitalbanking.loan.dto;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Data
@Builder
public class PrepaymentQuoteResponse {
    private UUID loanId;
    private BigDecimal outstandingPrincipal;
    private BigDecimal accruedInterest;
    private BigDecimal prepaymentPenalty;
    private BigDecimal netPayoffAmount;
    private LocalDate validUntil;
    private String currency;
}
