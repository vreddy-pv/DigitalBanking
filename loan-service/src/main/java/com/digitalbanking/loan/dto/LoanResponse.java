package com.digitalbanking.loan.dto;

import com.digitalbanking.loan.entity.Loan;
import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Data
@Builder
public class LoanResponse {
    private UUID loanId;
    private String userId;
    private String productType;
    private String productLine;
    private BigDecimal disbursedAmount;
    private BigDecimal outstandingPrincipal;
    private BigDecimal interestRate;
    private Integer tenureMonths;
    private BigDecimal emiAmount;
    private LocalDate nextDueDate;
    private String status;
    private String currency;
    private BigDecimal creditLimit;
    private BigDecimal utilisedAmount;
    private BigDecimal availableCredit;

    public static LoanResponse from(Loan loan) {
        LoanResponse.LoanResponseBuilder builder = LoanResponse.builder()
                .loanId(loan.getId())
                .userId(loan.getUserId())
                .productType(loan.getProductType().name())
                .productLine(loan.getProductLine().name())
                .disbursedAmount(loan.getDisbursedAmount())
                .outstandingPrincipal(loan.getOutstandingPrincipal())
                .interestRate(loan.getInterestRate())
                .tenureMonths(loan.getTenureMonths())
                .emiAmount(loan.getEmiAmount())
                .nextDueDate(loan.getNextDueDate())
                .status(loan.getStatus().name())
                .currency(loan.getCurrency())
                .creditLimit(loan.getCreditLimit())
                .utilisedAmount(loan.getUtilisedAmount());

        if (loan.getCreditLimit() != null && loan.getUtilisedAmount() != null) {
            builder.availableCredit(loan.getCreditLimit().subtract(loan.getUtilisedAmount()));
        }
        return builder.build();
    }
}
