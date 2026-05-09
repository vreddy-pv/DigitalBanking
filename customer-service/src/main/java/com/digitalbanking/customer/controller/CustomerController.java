package com.digitalbanking.customer.controller;

import com.digitalbanking.common.dto.ApiResponse;
import com.digitalbanking.customer.dto.*;
import com.digitalbanking.customer.service.CustomerService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/customers")
@RequiredArgsConstructor
public class CustomerController {

    private final CustomerService customerService;

    // -------------------------------------------------------------------------
    // KYC Document endpoints
    // -------------------------------------------------------------------------

    @GetMapping("/{customerId}/kyc/documents")
    public ResponseEntity<ApiResponse<List<KycDocumentResponse>>> getKycDocuments(
            @PathVariable UUID customerId) {
        List<KycDocumentResponse> documents = customerService.getKycDocuments(customerId);
        return ResponseEntity.ok(ApiResponse.<List<KycDocumentResponse>>builder()
                .success(true)
                .code("KYC_DOCUMENTS_RETRIEVED")
                .message("KYC documents retrieved successfully")
                .data(documents)
                .build());
    }

    @PostMapping("/{customerId}/kyc/documents")
    public ResponseEntity<ApiResponse<KycDocumentResponse>> submitKycDocument(
            @PathVariable UUID customerId,
            @Valid @RequestBody KycDocumentRequest request) {
        KycDocumentResponse document = customerService.submitKycDocument(customerId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.<KycDocumentResponse>builder()
                        .success(true)
                        .code("KYC_DOCUMENT_SUBMITTED")
                        .message("KYC document submitted successfully")
                        .data(document)
                        .build());
    }

    @PutMapping("/{customerId}/kyc/documents/{docId}/status")
    public ResponseEntity<ApiResponse<KycDocumentResponse>> updateKycDocumentStatus(
            @PathVariable UUID customerId,
            @PathVariable UUID docId,
            @Valid @RequestBody KycStatusUpdateRequest request) {
        KycDocumentResponse document = customerService.updateKycDocumentStatus(customerId, docId, request);
        return ResponseEntity.ok(ApiResponse.<KycDocumentResponse>builder()
                .success(true)
                .code("KYC_STATUS_UPDATED")
                .message("KYC document status updated successfully")
                .data(document)
                .build());
    }

    @GetMapping("/{customerId}/kyc/status")
    public ResponseEntity<ApiResponse<KycStatusSummaryResponse>> getKycStatus(
            @PathVariable UUID customerId) {
        KycStatusSummaryResponse summary = customerService.getKycStatus(customerId);
        return ResponseEntity.ok(ApiResponse.<KycStatusSummaryResponse>builder()
                .success(true)
                .code("KYC_STATUS_RETRIEVED")
                .message("KYC status retrieved successfully")
                .data(summary)
                .build());
    }

    // -------------------------------------------------------------------------
    // Beneficiary endpoints
    // -------------------------------------------------------------------------

    @GetMapping("/{customerId}/beneficiaries")
    public ResponseEntity<ApiResponse<List<BeneficiaryResponse>>> getBeneficiaries(
            @PathVariable UUID customerId) {
        List<BeneficiaryResponse> beneficiaries = customerService.getBeneficiaries(customerId);
        return ResponseEntity.ok(ApiResponse.<List<BeneficiaryResponse>>builder()
                .success(true)
                .code("BENEFICIARIES_RETRIEVED")
                .message("Beneficiaries retrieved successfully")
                .data(beneficiaries)
                .build());
    }

    @PostMapping("/{customerId}/beneficiaries")
    public ResponseEntity<ApiResponse<BeneficiaryResponse>> addBeneficiary(
            @PathVariable UUID customerId,
            @Valid @RequestBody BeneficiaryRequest request) {
        BeneficiaryResponse beneficiary = customerService.addBeneficiary(customerId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.<BeneficiaryResponse>builder()
                        .success(true)
                        .code("BENEFICIARY_ADDED")
                        .message("Beneficiary added successfully")
                        .data(beneficiary)
                        .build());
    }

    @DeleteMapping("/{customerId}/beneficiaries/{beneficiaryId}")
    public ResponseEntity<ApiResponse<Void>> removeBeneficiary(
            @PathVariable UUID customerId,
            @PathVariable UUID beneficiaryId) {
        customerService.removeBeneficiary(customerId, beneficiaryId);
        return ResponseEntity.ok(ApiResponse.<Void>builder()
                .success(true)
                .code("BENEFICIARY_REMOVED")
                .message("Beneficiary removed successfully")
                .build());
    }

    // -------------------------------------------------------------------------
    // Preferences endpoints
    // -------------------------------------------------------------------------

    @GetMapping("/{customerId}/preferences")
    public ResponseEntity<ApiResponse<CustomerPreferencesResponse>> getPreferences(
            @PathVariable UUID customerId) {
        CustomerPreferencesResponse preferences = customerService.getPreferences(customerId);
        return ResponseEntity.ok(ApiResponse.<CustomerPreferencesResponse>builder()
                .success(true)
                .code("PREFERENCES_RETRIEVED")
                .message("Customer preferences retrieved successfully")
                .data(preferences)
                .build());
    }

    @PutMapping("/{customerId}/preferences")
    public ResponseEntity<ApiResponse<CustomerPreferencesResponse>> updatePreferences(
            @PathVariable UUID customerId,
            @Valid @RequestBody CustomerPreferencesRequest request) {
        CustomerPreferencesResponse preferences = customerService.updatePreferences(customerId, request);
        return ResponseEntity.ok(ApiResponse.<CustomerPreferencesResponse>builder()
                .success(true)
                .code("PREFERENCES_UPDATED")
                .message("Customer preferences updated successfully")
                .data(preferences)
                .build());
    }
}
