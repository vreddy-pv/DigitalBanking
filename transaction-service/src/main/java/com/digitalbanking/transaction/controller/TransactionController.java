package com.digitalbanking.transaction.controller;

import com.digitalbanking.transaction.dto.DepositRequest;
import com.digitalbanking.transaction.dto.TransactionResponse;
import com.digitalbanking.transaction.dto.TransferRequest;
import com.digitalbanking.transaction.dto.WithdrawalRequest;
import com.digitalbanking.transaction.service.TransactionService;
import com.digitalbanking.common.dto.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/transactions")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService transactionService;

    @PostMapping("/deposit")
    public ResponseEntity<ApiResponse<TransactionResponse>> deposit(
            @Valid @RequestBody DepositRequest request) {
        TransactionResponse transaction = transactionService.deposit(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.<TransactionResponse>builder()
                        .success(true)
                        .code("DEPOSIT_CREATED")
                        .message("Deposit transaction created successfully")
                        .data(transaction)
                        .transactionId(transaction.getId().toString())
                        .build());
    }

    @PostMapping("/withdraw")
    public ResponseEntity<ApiResponse<TransactionResponse>> withdraw(
            @Valid @RequestBody WithdrawalRequest request) {
        TransactionResponse transaction = transactionService.withdraw(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.<TransactionResponse>builder()
                        .success(true)
                        .code("WITHDRAWAL_CREATED")
                        .message("Withdrawal transaction created successfully")
                        .data(transaction)
                        .transactionId(transaction.getId().toString())
                        .build());
    }

    @PostMapping("/transfer")
    public ResponseEntity<ApiResponse<TransactionResponse>> transfer(
            @Valid @RequestBody TransferRequest request) {
        TransactionResponse transaction = transactionService.transfer(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.<TransactionResponse>builder()
                        .success(true)
                        .code("TRANSFER_CREATED")
                        .message("Transfer transaction created successfully")
                        .data(transaction)
                        .transactionId(transaction.getId().toString())
                        .build());
    }

    @GetMapping("/{transactionId}")
    public ResponseEntity<ApiResponse<TransactionResponse>> getTransaction(
            @PathVariable UUID transactionId) {
        TransactionResponse transaction = transactionService.getTransactionById(transactionId);
        return ResponseEntity.ok(ApiResponse.<TransactionResponse>builder()
                .success(true)
                .code("TRANSACTION_RETRIEVED")
                .message("Transaction retrieved successfully")
                .data(transaction)
                .transactionId(transactionId.toString())
                .build());
    }

    @GetMapping("/account/{accountId}")
    public ResponseEntity<ApiResponse<List<TransactionResponse>>> getAccountTransactions(
            @PathVariable UUID accountId) {
        List<TransactionResponse> transactions = transactionService.getTransactionsByAccountId(accountId);
        return ResponseEntity.ok(ApiResponse.<List<TransactionResponse>>builder()
                .success(true)
                .code("TRANSACTIONS_RETRIEVED")
                .message("Account transactions retrieved successfully")
                .data(transactions)
                .build());
    }

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        return ResponseEntity.ok(ApiResponse.<String>builder()
                .success(true)
                .code("SERVICE_HEALTHY")
                .message("Transaction Service is healthy")
                .data("UP")
                .build());
    }
}
