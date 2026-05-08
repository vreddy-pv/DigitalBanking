package com.digitalbanking.account.controller;

import com.digitalbanking.account.dto.AccountResponse;
import com.digitalbanking.account.dto.CustomerRegistrationRequest;
import com.digitalbanking.account.dto.CustomerResponse;
import com.digitalbanking.account.service.AccountService;
import com.digitalbanking.common.dto.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/accounts")
@RequiredArgsConstructor
public class AccountController {

    private final AccountService accountService;

    @PostMapping("/register")
    public ResponseEntity<ApiResponse<CustomerResponse>> registerCustomer(
            @Valid @RequestBody CustomerRegistrationRequest request) {
        CustomerResponse customer = accountService.registerCustomer(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.<CustomerResponse>builder()
                        .success(true)
                        .code("CUSTOMER_REGISTERED")
                        .message("Customer registered successfully")
                        .data(customer)
                        .build());
    }

    @GetMapping("/{accountId}")
    public ResponseEntity<ApiResponse<AccountResponse>> getAccount(@PathVariable UUID accountId) {
        AccountResponse account = accountService.getAccountById(accountId);
        return ResponseEntity.ok(ApiResponse.<AccountResponse>builder()
                .success(true)
                .code("ACCOUNT_RETRIEVED")
                .message("Account retrieved successfully")
                .data(account)
                .build());
    }

    @GetMapping("/number/{accountNumber}")
    public ResponseEntity<ApiResponse<AccountResponse>> getAccountByNumber(
            @PathVariable String accountNumber) {
        AccountResponse account = accountService.getAccountByNumber(accountNumber);
        return ResponseEntity.ok(ApiResponse.<AccountResponse>builder()
                .success(true)
                .code("ACCOUNT_RETRIEVED")
                .message("Account retrieved successfully")
                .data(account)
                .build());
    }

    @GetMapping("/customer/{customerId}")
    public ResponseEntity<ApiResponse<CustomerResponse>> getCustomer(@PathVariable UUID customerId) {
        CustomerResponse customer = accountService.getCustomerById(customerId);
        return ResponseEntity.ok(ApiResponse.<CustomerResponse>builder()
                .success(true)
                .code("CUSTOMER_RETRIEVED")
                .message("Customer retrieved successfully")
                .data(customer)
                .build());
    }

    @GetMapping("/customer/user/{userId}")
    public ResponseEntity<ApiResponse<CustomerResponse>> getCustomerByUserId(@PathVariable UUID userId) {
        CustomerResponse customer = accountService.getCustomerByUserId(userId);
        return ResponseEntity.ok(ApiResponse.<CustomerResponse>builder()
                .success(true)
                .code("CUSTOMER_RETRIEVED")
                .message("Customer retrieved successfully")
                .data(customer)
                .build());
    }

    @GetMapping("/customer/{customerId}/accounts")
    public ResponseEntity<ApiResponse<List<AccountResponse>>> getCustomerAccounts(
            @PathVariable UUID customerId) {
        List<AccountResponse> accounts = accountService.getAccountsByCustomerId(customerId);
        return ResponseEntity.ok(ApiResponse.<List<AccountResponse>>builder()
                .success(true)
                .code("ACCOUNTS_RETRIEVED")
                .message("Customer accounts retrieved successfully")
                .data(accounts)
                .build());
    }

    @PutMapping("/customer/{customerId}/profile")
    public ResponseEntity<ApiResponse<CustomerResponse>> updateCustomerProfile(
            @PathVariable UUID customerId,
            @Valid @RequestBody CustomerRegistrationRequest request) {
        CustomerResponse customer = accountService.updateCustomerProfile(customerId, request);
        return ResponseEntity.ok(ApiResponse.<CustomerResponse>builder()
                .success(true)
                .code("CUSTOMER_UPDATED")
                .message("Customer profile updated successfully")
                .data(customer)
                .build());
    }

    @PutMapping("/{accountId}/status")
    public ResponseEntity<ApiResponse<Void>> updateAccountStatus(
            @PathVariable UUID accountId,
            @RequestParam String status) {
        accountService.updateAccountStatus(accountId, status);
        return ResponseEntity.ok(ApiResponse.<Void>builder()
                .success(true)
                .code("ACCOUNT_STATUS_UPDATED")
                .message("Account status updated successfully")
                .build());
    }

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        return ResponseEntity.ok(ApiResponse.<String>builder()
                .success(true)
                .code("SERVICE_HEALTHY")
                .message("Account Service is healthy")
                .data("UP")
                .build());
    }
}
