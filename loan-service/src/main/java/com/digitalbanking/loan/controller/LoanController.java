package com.digitalbanking.loan.controller;

import com.digitalbanking.common.dto.ApiResponse;
import com.digitalbanking.loan.dto.*;
import com.digitalbanking.loan.service.LoanService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/loans")
@RequiredArgsConstructor
public class LoanController {

    private final LoanService loanService;

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        return ResponseEntity.ok(ApiResponse.<String>builder()
                .success(true)
                .code("SERVICE_HEALTHY")
                .message("Loan Service is healthy")
                .data("UP")
                .build());
    }

    // ── Mortgage Loans (ML) ──────────────────────────────────────────────────

    @GetMapping("/{userId}/mortgage")
    public ResponseEntity<ApiResponse<List<LoanResponse>>> getMortgageLoans(
            @PathVariable String userId) {
        List<LoanResponse> loans = loanService.getMortgageLoans(userId);
        return ResponseEntity.ok(ApiResponse.<List<LoanResponse>>builder()
                .success(true)
                .code("LOANS_RETRIEVED")
                .message("Mortgage loans retrieved for user " + userId)
                .data(loans)
                .build());
    }

    @GetMapping("/{loanId}/emi-schedule")
    public ResponseEntity<ApiResponse<List<EmiScheduleResponse>>> getEmiSchedule(
            @PathVariable UUID loanId,
            @RequestParam(defaultValue = "3") int upcomingMonths) {
        List<EmiScheduleResponse> schedule = loanService.getEmiSchedule(loanId, upcomingMonths);
        return ResponseEntity.ok(ApiResponse.<List<EmiScheduleResponse>>builder()
                .success(true)
                .code("EMI_SCHEDULE_RETRIEVED")
                .message("EMI schedule retrieved")
                .data(schedule)
                .build());
    }

    @GetMapping("/{loanId}/prepayment-quote")
    public ResponseEntity<ApiResponse<PrepaymentQuoteResponse>> getPrepaymentQuote(
            @PathVariable UUID loanId) {
        PrepaymentQuoteResponse quote = loanService.getPrepaymentQuote(loanId);
        return ResponseEntity.ok(ApiResponse.<PrepaymentQuoteResponse>builder()
                .success(true)
                .code("PREPAYMENT_QUOTE_RETRIEVED")
                .message("Prepayment quote valid for 7 days")
                .data(quote)
                .build());
    }

    // ── Unsecured Loans (USL) ────────────────────────────────────────────────

    @GetMapping("/{userId}/unsecured")
    public ResponseEntity<ApiResponse<List<LoanResponse>>> getUnsecuredLoans(
            @PathVariable String userId) {
        List<LoanResponse> loans = loanService.getUnsecuredLoans(userId);
        return ResponseEntity.ok(ApiResponse.<List<LoanResponse>>builder()
                .success(true)
                .code("LOANS_RETRIEVED")
                .message("Unsecured loans retrieved for user " + userId)
                .data(loans)
                .build());
    }

    @GetMapping("/{loanId}/payment-due")
    public ResponseEntity<ApiResponse<PaymentDueResponse>> getPaymentDue(
            @PathVariable UUID loanId) {
        PaymentDueResponse due = loanService.getPaymentDue(loanId);
        return ResponseEntity.ok(ApiResponse.<PaymentDueResponse>builder()
                .success(true)
                .code("PAYMENT_DUE_RETRIEVED")
                .message("Payment due details retrieved")
                .data(due)
                .build());
    }

    @GetMapping("/{loanId}/credit-limit")
    public ResponseEntity<ApiResponse<CreditLimitResponse>> getCreditLimit(
            @PathVariable UUID loanId) {
        CreditLimitResponse limit = loanService.getCreditLimit(loanId);
        return ResponseEntity.ok(ApiResponse.<CreditLimitResponse>builder()
                .success(true)
                .code("CREDIT_LIMIT_RETRIEVED")
                .message("Credit limit details retrieved")
                .data(limit)
                .build());
    }
}
