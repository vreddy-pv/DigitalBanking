package com.digitalbanking.loan.service;

import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.loan.dto.*;
import com.digitalbanking.loan.entity.EmiSchedule;
import com.digitalbanking.loan.entity.Loan;
import com.digitalbanking.loan.repository.EmiScheduleRepository;
import com.digitalbanking.loan.repository.LoanRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class LoanService {

    private final LoanRepository loanRepository;
    private final EmiScheduleRepository emiScheduleRepository;

    @Transactional(readOnly = true)
    public List<LoanResponse> getMortgageLoans(String userId) {
        return loanRepository
                .findByUserIdAndProductLineOrderByCreatedAtDesc(userId, Loan.ProductLine.ML)
                .stream()
                .map(LoanResponse::from)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<LoanResponse> getUnsecuredLoans(String userId) {
        return loanRepository
                .findByUserIdAndProductLineOrderByCreatedAtDesc(userId, Loan.ProductLine.USL)
                .stream()
                .map(LoanResponse::from)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<EmiScheduleResponse> getEmiSchedule(UUID loanId, int upcomingMonths) {
        Loan loan = findLoan(loanId);
        List<EmiSchedule> schedule = emiScheduleRepository
                .findByLoanIdAndDueDateGreaterThanEqualOrderByDueDateAsc(loanId, LocalDate.now());

        return schedule.stream()
                .limit(upcomingMonths)
                .map(emi -> EmiScheduleResponse.from(emi, loan.getCurrency()))
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public PrepaymentQuoteResponse getPrepaymentQuote(UUID loanId) {
        Loan loan = findLoan(loanId);
        // Daily interest = outstanding * annual_rate / 365
        BigDecimal dailyRate = loan.getInterestRate()
                .divide(BigDecimal.valueOf(36500), 10, RoundingMode.HALF_UP);
        BigDecimal accruedInterest = loan.getOutstandingPrincipal()
                .multiply(dailyRate)
                .multiply(BigDecimal.valueOf(30))
                .setScale(2, RoundingMode.HALF_UP);

        return PrepaymentQuoteResponse.builder()
                .loanId(loan.getId())
                .outstandingPrincipal(loan.getOutstandingPrincipal())
                .accruedInterest(accruedInterest)
                .prepaymentPenalty(BigDecimal.ZERO)
                .netPayoffAmount(loan.getOutstandingPrincipal().add(accruedInterest))
                .validUntil(LocalDate.now().plusDays(7))
                .currency(loan.getCurrency())
                .build();
    }

    @Transactional(readOnly = true)
    public PaymentDueResponse getPaymentDue(UUID loanId) {
        Loan loan = findLoan(loanId);
        return PaymentDueResponse.builder()
                .loanId(loan.getId())
                .productType(loan.getProductType().name())
                .nextDueDate(loan.getNextDueDate())
                .minimumPayment(loan.getEmiAmount() != null ? loan.getEmiAmount() : BigDecimal.ZERO)
                .totalOutstanding(loan.getOutstandingPrincipal())
                .overdueAmount(BigDecimal.ZERO)
                .currency(loan.getCurrency())
                .build();
    }

    @Transactional(readOnly = true)
    public CreditLimitResponse getCreditLimit(UUID loanId) {
        Loan loan = findLoan(loanId);
        if (loan.getCreditLimit() == null) {
            throw new AppException("NOT_A_REVOLVING_PRODUCT",
                    "Loan " + loanId + " is not a revolving product (credit card or overdraft).");
        }
        BigDecimal available = loan.getCreditLimit()
                .subtract(loan.getUtilisedAmount() != null ? loan.getUtilisedAmount() : BigDecimal.ZERO);
        return CreditLimitResponse.builder()
                .loanId(loan.getId())
                .productType(loan.getProductType().name())
                .creditLimit(loan.getCreditLimit())
                .utilisedAmount(loan.getUtilisedAmount())
                .availableCredit(available)
                .currency(loan.getCurrency())
                .build();
    }

    private Loan findLoan(UUID loanId) {
        return loanRepository.findById(loanId)
                .orElseThrow(() -> new AppException("LOAN_NOT_FOUND",
                        "Loan not found: " + loanId));
    }
}
