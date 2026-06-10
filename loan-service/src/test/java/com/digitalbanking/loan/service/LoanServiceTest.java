package com.digitalbanking.loan.service;

import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.loan.dto.*;
import com.digitalbanking.loan.entity.EmiSchedule;
import com.digitalbanking.loan.entity.Loan;
import com.digitalbanking.loan.repository.EmiScheduleRepository;
import com.digitalbanking.loan.repository.LoanRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class LoanServiceTest {

    @Mock private LoanRepository loanRepository;
    @Mock private EmiScheduleRepository emiScheduleRepository;
    @InjectMocks private LoanService loanService;

    @Test
    void getMortgageLoans_returnsMlLoans() {
        Loan loan = buildLoan(Loan.ProductType.HOME_LOAN, Loan.ProductLine.ML);
        when(loanRepository.findByUserIdAndProductLineOrderByCreatedAtDesc("user-1", Loan.ProductLine.ML))
                .thenReturn(List.of(loan));

        List<LoanResponse> result = loanService.getMortgageLoans("user-1");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getProductLine()).isEqualTo("ML");
        assertThat(result.get(0).getProductType()).isEqualTo("HOME_LOAN");
    }

    @Test
    void getUnsecuredLoans_returnsUslLoans() {
        Loan loan = buildLoan(Loan.ProductType.PERSONAL_LOAN, Loan.ProductLine.USL);
        when(loanRepository.findByUserIdAndProductLineOrderByCreatedAtDesc("user-1", Loan.ProductLine.USL))
                .thenReturn(List.of(loan));

        List<LoanResponse> result = loanService.getUnsecuredLoans("user-1");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getProductLine()).isEqualTo("USL");
    }

    @Test
    void getEmiSchedule_returnsUpcomingEmis() {
        UUID loanId = UUID.randomUUID();
        Loan loan = buildLoanWithId(loanId, Loan.ProductType.HOME_LOAN, Loan.ProductLine.ML);
        EmiSchedule emi = buildEmi(loan, LocalDate.now().plusMonths(1));

        when(loanRepository.findById(loanId)).thenReturn(Optional.of(loan));
        when(emiScheduleRepository.findByLoanIdAndDueDateGreaterThanEqualOrderByDueDateAsc(eq(loanId), any()))
                .thenReturn(List.of(emi));

        List<EmiScheduleResponse> result = loanService.getEmiSchedule(loanId, 3);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getEmiAmount()).isEqualByComparingTo("44067.00");
    }

    @Test
    void getPrepaymentQuote_calculatesAccruedInterest() {
        UUID loanId = UUID.randomUUID();
        Loan loan = buildLoanWithId(loanId, Loan.ProductType.HOME_LOAN, Loan.ProductLine.ML);
        when(loanRepository.findById(loanId)).thenReturn(Optional.of(loan));

        PrepaymentQuoteResponse result = loanService.getPrepaymentQuote(loanId);

        assertThat(result.getLoanId()).isEqualTo(loanId);
        assertThat(result.getOutstandingPrincipal()).isEqualByComparingTo("4250000.00");
        assertThat(result.getPrepaymentPenalty()).isEqualByComparingTo("0");
        assertThat(result.getNetPayoffAmount()).isGreaterThan(result.getOutstandingPrincipal());
        assertThat(result.getValidUntil()).isEqualTo(LocalDate.now().plusDays(7));
    }

    @Test
    void getPaymentDue_returnsDueInfo() {
        UUID loanId = UUID.randomUUID();
        Loan loan = buildLoanWithId(loanId, Loan.ProductType.PERSONAL_LOAN, Loan.ProductLine.USL);
        when(loanRepository.findById(loanId)).thenReturn(Optional.of(loan));

        PaymentDueResponse result = loanService.getPaymentDue(loanId);

        assertThat(result.getLoanId()).isEqualTo(loanId);
        assertThat(result.getMinimumPayment()).isEqualByComparingTo("44067.00");
        assertThat(result.getTotalOutstanding()).isEqualByComparingTo("4250000.00");
    }

    @Test
    void getCreditLimit_creditCardLoan_returnsCreditInfo() {
        UUID loanId = UUID.randomUUID();
        Loan loan = buildLoanWithId(loanId, Loan.ProductType.CREDIT_CARD, Loan.ProductLine.USL);
        loan.setCreditLimit(new BigDecimal("200000.00"));
        loan.setUtilisedAmount(new BigDecimal("45000.00"));
        when(loanRepository.findById(loanId)).thenReturn(Optional.of(loan));

        CreditLimitResponse result = loanService.getCreditLimit(loanId);

        assertThat(result.getCreditLimit()).isEqualByComparingTo("200000.00");
        assertThat(result.getUtilisedAmount()).isEqualByComparingTo("45000.00");
        assertThat(result.getAvailableCredit()).isEqualByComparingTo("155000.00");
    }

    @Test
    void getCreditLimit_nonRevolvingLoan_throwsException() {
        UUID loanId = UUID.randomUUID();
        Loan loan = buildLoanWithId(loanId, Loan.ProductType.HOME_LOAN, Loan.ProductLine.ML);
        when(loanRepository.findById(loanId)).thenReturn(Optional.of(loan));

        assertThatThrownBy(() -> loanService.getCreditLimit(loanId))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("not a revolving product");
    }

    @Test
    void findLoan_notFound_throwsException() {
        UUID loanId = UUID.randomUUID();
        when(loanRepository.findById(loanId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> loanService.getPaymentDue(loanId))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("Loan not found");
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private Loan buildLoan(Loan.ProductType type, Loan.ProductLine line) {
        return buildLoanWithId(UUID.randomUUID(), type, line);
    }

    private Loan buildLoanWithId(UUID id, Loan.ProductType type, Loan.ProductLine line) {
        Loan loan = new Loan();
        loan.setId(id);
        loan.setUserId("user-1");
        loan.setCustomerId("cust-1");
        loan.setProductType(type);
        loan.setProductLine(line);
        loan.setDisbursedAmount(new BigDecimal("5000000.00"));
        loan.setOutstandingPrincipal(new BigDecimal("4250000.00"));
        loan.setInterestRate(new BigDecimal("8.65"));
        loan.setTenureMonths(240);
        loan.setEmiAmount(new BigDecimal("44067.00"));
        loan.setNextDueDate(LocalDate.now().plusMonths(1));
        loan.setStatus(Loan.LoanStatus.ACTIVE);
        loan.setCurrency("INR");
        loan.setCreatedAt(OffsetDateTime.now());
        loan.setUpdatedAt(OffsetDateTime.now());
        return loan;
    }

    private EmiSchedule buildEmi(Loan loan, LocalDate dueDate) {
        EmiSchedule emi = new EmiSchedule();
        emi.setId(UUID.randomUUID());
        emi.setLoan(loan);
        emi.setDueDate(dueDate);
        emi.setEmiAmount(new BigDecimal("44067.00"));
        emi.setPrincipalComponent(new BigDecimal("12500.00"));
        emi.setInterestComponent(new BigDecimal("31567.00"));
        emi.setBalanceAfter(new BigDecimal("4237500.00"));
        emi.setStatus(EmiSchedule.EmiStatus.PENDING);
        return emi;
    }
}
