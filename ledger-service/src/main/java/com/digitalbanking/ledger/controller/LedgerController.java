package com.digitalbanking.ledger.controller;

import com.digitalbanking.ledger.dto.GLAccountResponse;
import com.digitalbanking.ledger.dto.JournalEntryResponse;
import com.digitalbanking.ledger.service.LedgerService;
import com.digitalbanking.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/ledger")
@RequiredArgsConstructor
public class LedgerController {

    private final LedgerService ledgerService;

    @PostMapping("/initialize")
    public ResponseEntity<ApiResponse<Void>> initializeGLAccounts() {
        ledgerService.initializeGLAccounts();
        return ResponseEntity.ok(ApiResponse.<Void>builder()
                .success(true)
                .code("GL_ACCOUNTS_INITIALIZED")
                .message("GL accounts initialized successfully")
                .build());
    }

    @GetMapping("/accounts")
    public ResponseEntity<ApiResponse<List<GLAccountResponse>>> getAllGLAccounts() {
        List<GLAccountResponse> accounts = ledgerService.getAllGLAccounts();
        return ResponseEntity.ok(ApiResponse.<List<GLAccountResponse>>builder()
                .success(true)
                .code("GL_ACCOUNTS_RETRIEVED")
                .message("GL accounts retrieved successfully")
                .data(accounts)
                .build());
    }

    @GetMapping("/accounts/{accountId}")
    public ResponseEntity<ApiResponse<GLAccountResponse>> getGLAccountBalance(@PathVariable UUID accountId) {
        GLAccountResponse account = ledgerService.getGLAccountBalance(accountId);
        return ResponseEntity.ok(ApiResponse.<GLAccountResponse>builder()
                .success(true)
                .code("GL_ACCOUNT_RETRIEVED")
                .message("GL account retrieved successfully")
                .data(account)
                .build());
    }

    @GetMapping("/journal/{transactionId}")
    public ResponseEntity<ApiResponse<List<JournalEntryResponse>>> getJournalEntries(@PathVariable UUID transactionId) {
        List<JournalEntryResponse> entries = ledgerService.getJournalEntriesByTransaction(transactionId);
        return ResponseEntity.ok(ApiResponse.<List<JournalEntryResponse>>builder()
                .success(true)
                .code("JOURNAL_ENTRIES_RETRIEVED")
                .message("Journal entries retrieved successfully")
                .data(entries)
                .build());
    }

    @GetMapping("/trial-balance")
    public ResponseEntity<ApiResponse<String>> getTrialBalance() {
        String trialBalance = ledgerService.getTrialBalance();
        return ResponseEntity.ok(ApiResponse.<String>builder()
                .success(true)
                .code("TRIAL_BALANCE_RETRIEVED")
                .message("Trial balance retrieved successfully")
                .data(trialBalance)
                .build());
    }

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        return ResponseEntity.ok(ApiResponse.<String>builder()
                .success(true)
                .code("SERVICE_HEALTHY")
                .message("Ledger Service is healthy")
                .data("UP")
                .build());
    }
}
