package com.digitalbanking.loan.dto;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Data
@Builder
public class PaymentDueResponse {
    private UUID loanId;
    private String productType;
    private LocalDate nextDueDate;
    private BigDecimal minimumPayment;
    private BigDecimal totalOutstanding;
    private BigDecimal overdueAmount;
    private String currency;
}
