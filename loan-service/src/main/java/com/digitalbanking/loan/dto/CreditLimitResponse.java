package com.digitalbanking.loan.dto;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.util.UUID;

@Data
@Builder
public class CreditLimitResponse {
    private UUID loanId;
    private String productType;
    private BigDecimal creditLimit;
    private BigDecimal utilisedAmount;
    private BigDecimal availableCredit;
    private String currency;
}
