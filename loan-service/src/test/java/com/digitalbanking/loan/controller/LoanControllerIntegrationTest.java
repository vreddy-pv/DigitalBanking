package com.digitalbanking.loan.controller;

import com.digitalbanking.loan.entity.EmiSchedule;
import com.digitalbanking.loan.entity.Loan;
import com.digitalbanking.loan.repository.EmiScheduleRepository;
import com.digitalbanking.loan.repository.LoanRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class LoanControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("loan_db")
            .withUsername("postgres")
            .withPassword("password");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired private MockMvc mockMvc;
    @Autowired private LoanRepository loanRepository;
    @Autowired private EmiScheduleRepository emiScheduleRepository;

    @BeforeEach
    void cleanUp() {
        emiScheduleRepository.deleteAll();
        loanRepository.deleteAll();
    }

    @Test
    void health_returns200() throws Exception {
        mockMvc.perform(get("/api/v1/loans/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").value("UP"));
    }

    @Test
    void getMortgageLoans_returnsListForUser() throws Exception {
        Loan loan = saveLoan("user-it-01", Loan.ProductType.HOME_LOAN, Loan.ProductLine.ML);

        mockMvc.perform(get("/api/v1/loans/{userId}/mortgage", "user-it-01"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].productType").value("HOME_LOAN"));
    }

    @Test
    void getMortgageLoans_emptyForUnknownUser_returnsEmptyList() throws Exception {
        mockMvc.perform(get("/api/v1/loans/{userId}/mortgage", "no-such-user"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(0)));
    }

    @Test
    void getUnsecuredLoans_returnsPersonalLoan() throws Exception {
        saveLoan("user-it-02", Loan.ProductType.PERSONAL_LOAN, Loan.ProductLine.USL);

        mockMvc.perform(get("/api/v1/loans/{userId}/unsecured", "user-it-02"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data[0].productLine").value("USL"));
    }

    @Test
    void getEmiSchedule_returnsUpcomingEmis() throws Exception {
        Loan loan = saveLoan("user-it-03", Loan.ProductType.HOME_LOAN, Loan.ProductLine.ML);
        saveEmi(loan, LocalDate.now().plusMonths(1));
        saveEmi(loan, LocalDate.now().plusMonths(2));

        mockMvc.perform(get("/api/v1/loans/{loanId}/emi-schedule", loan.getId())
                        .param("upcomingMonths", "2"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(2)));
    }

    @Test
    void getPrepaymentQuote_returnsQuote() throws Exception {
        Loan loan = saveLoan("user-it-04", Loan.ProductType.HOME_LOAN, Loan.ProductLine.ML);

        mockMvc.perform(get("/api/v1/loans/{loanId}/prepayment-quote", loan.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.outstandingPrincipal").value(4250000.0))
                .andExpect(jsonPath("$.data.prepaymentPenalty").value(0));
    }

    @Test
    void getPaymentDue_returnsPaymentInfo() throws Exception {
        Loan loan = saveLoan("user-it-05", Loan.ProductType.PERSONAL_LOAN, Loan.ProductLine.USL);

        mockMvc.perform(get("/api/v1/loans/{loanId}/payment-due", loan.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.minimumPayment").value(44067.0));
    }

    @Test
    void getCreditLimit_creditCard_returnsCreditInfo() throws Exception {
        Loan loan = saveLoan("user-it-06", Loan.ProductType.CREDIT_CARD, Loan.ProductLine.USL);
        loan.setCreditLimit(new BigDecimal("200000.00"));
        loan.setUtilisedAmount(new BigDecimal("45000.00"));
        loanRepository.save(loan);

        mockMvc.perform(get("/api/v1/loans/{loanId}/credit-limit", loan.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.creditLimit").value(200000.0))
                .andExpect(jsonPath("$.data.availableCredit").value(155000.0));
    }

    @Test
    void getCreditLimit_nonRevolvingLoan_returns400() throws Exception {
        Loan loan = saveLoan("user-it-07", Loan.ProductType.HOME_LOAN, Loan.ProductLine.ML);

        mockMvc.perform(get("/api/v1/loans/{loanId}/credit-limit", loan.getId()))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false));
    }

    @Test
    void getLoan_notFound_returns404() throws Exception {
        mockMvc.perform(get("/api/v1/loans/{loanId}/payment-due",
                        "00000000-0000-0000-0000-000000000000"))
                .andExpect(status().isNotFound());
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private Loan saveLoan(String userId, Loan.ProductType type, Loan.ProductLine line) {
        Loan loan = new Loan();
        loan.setUserId(userId);
        loan.setCustomerId("cust-test");
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
        return loanRepository.save(loan);
    }

    private EmiSchedule saveEmi(Loan loan, LocalDate dueDate) {
        EmiSchedule emi = new EmiSchedule();
        emi.setLoan(loan);
        emi.setDueDate(dueDate);
        emi.setEmiAmount(new BigDecimal("44067.00"));
        emi.setPrincipalComponent(new BigDecimal("12500.00"));
        emi.setInterestComponent(new BigDecimal("31567.00"));
        emi.setBalanceAfter(new BigDecimal("4237500.00"));
        emi.setStatus(EmiSchedule.EmiStatus.PENDING);
        return emiScheduleRepository.save(emi);
    }
}
