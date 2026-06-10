package com.digitalbanking.loan.dto;

import com.digitalbanking.loan.entity.EmiSchedule;
import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Data
@Builder
public class EmiScheduleResponse {
    private UUID loanId;
    private LocalDate dueDate;
    private BigDecimal emiAmount;
    private BigDecimal principalComponent;
    private BigDecimal interestComponent;
    private BigDecimal balanceAfter;
    private String status;
    private String currency;

    public static EmiScheduleResponse from(EmiSchedule emi, String currency) {
        return EmiScheduleResponse.builder()
                .loanId(emi.getLoan().getId())
                .dueDate(emi.getDueDate())
                .emiAmount(emi.getEmiAmount())
                .principalComponent(emi.getPrincipalComponent())
                .interestComponent(emi.getInterestComponent())
                .balanceAfter(emi.getBalanceAfter())
                .status(emi.getStatus().name())
                .currency(currency)
                .build();
    }
}
