package com.digitalbanking.customer.service;

import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.customer.dto.*;
import com.digitalbanking.customer.entity.Beneficiary;
import com.digitalbanking.customer.entity.CustomerPreferences;
import com.digitalbanking.customer.entity.KycDocument;
import com.digitalbanking.customer.repository.BeneficiaryRepository;
import com.digitalbanking.customer.repository.CustomerPreferencesRepository;
import com.digitalbanking.customer.repository.KycDocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class CustomerService {

    private final KycDocumentRepository kycDocumentRepository;
    private final BeneficiaryRepository beneficiaryRepository;
    private final CustomerPreferencesRepository customerPreferencesRepository;

    // -------------------------------------------------------------------------
    // KYC Documents
    // -------------------------------------------------------------------------

    @Transactional(readOnly = true)
    public List<KycDocumentResponse> getKycDocuments(UUID customerId) {
        log.info("Fetching KYC documents for customer: {}", customerId);
        return kycDocumentRepository.findByCustomerIdOrderByCreatedAtDesc(customerId)
                .stream()
                .map(this::mapToKycResponse)
                .collect(Collectors.toList());
    }

    public KycDocumentResponse submitKycDocument(UUID customerId, KycDocumentRequest request) {
        log.info("Submitting KYC document for customer: {}, type: {}", customerId, request.getDocumentType());

        KycDocument document = KycDocument.builder()
                .customerId(customerId)
                .documentType(request.getDocumentType())
                .documentReference(request.getDocumentReference())
                .status("PENDING")
                .build();

        document = kycDocumentRepository.save(document);
        log.info("KYC document submitted: {} for customer: {}", document.getId(), customerId);
        return mapToKycResponse(document);
    }

    public KycDocumentResponse updateKycDocumentStatus(UUID customerId, UUID docId, KycStatusUpdateRequest request) {
        log.info("Updating KYC document status: {} to {} for customer: {}", docId, request.getStatus(), customerId);

        KycDocument document = kycDocumentRepository.findById(docId)
                .orElseThrow(() -> new AppException("KYC_DOCUMENT_NOT_FOUND", "KYC document not found: " + docId));

        if (!document.getCustomerId().equals(customerId)) {
            throw new AppException("KYC_DOCUMENT_NOT_FOUND", "KYC document not found for customer: " + customerId);
        }

        if ("REJECTED".equals(request.getStatus()) &&
                (request.getRejectionReason() == null || request.getRejectionReason().isBlank())) {
            throw new AppException("REJECTION_REASON_REQUIRED", "Rejection reason is required when rejecting a document");
        }

        document.setStatus(request.getStatus());
        document.setReviewedAt(LocalDateTime.now());
        if ("REJECTED".equals(request.getStatus())) {
            document.setRejectionReason(request.getRejectionReason());
        } else {
            document.setRejectionReason(null);
        }

        document = kycDocumentRepository.save(document);
        log.info("KYC document {} updated to status: {}", docId, request.getStatus());
        return mapToKycResponse(document);
    }

    @Transactional(readOnly = true)
    public KycStatusSummaryResponse getKycStatus(UUID customerId) {
        log.info("Fetching KYC status summary for customer: {}", customerId);

        long total = kycDocumentRepository.countByCustomerId(customerId);
        long pending = kycDocumentRepository.countByCustomerIdAndStatus(customerId, "PENDING");
        long verified = kycDocumentRepository.countByCustomerIdAndStatus(customerId, "VERIFIED");
        long rejected = kycDocumentRepository.countByCustomerIdAndStatus(customerId, "REJECTED");

        String overallStatus;
        if (total == 0) {
            overallStatus = "NO_DOCUMENTS";
        } else if (rejected > 0) {
            overallStatus = "REJECTED";
        } else if (pending > 0) {
            overallStatus = "PENDING";
        } else {
            overallStatus = "VERIFIED";
        }

        return KycStatusSummaryResponse.builder()
                .customerId(customerId)
                .totalDocuments((int) total)
                .pendingDocuments((int) pending)
                .verifiedDocuments((int) verified)
                .rejectedDocuments((int) rejected)
                .overallStatus(overallStatus)
                .build();
    }

    // -------------------------------------------------------------------------
    // Beneficiaries
    // -------------------------------------------------------------------------

    @Transactional(readOnly = true)
    public List<BeneficiaryResponse> getBeneficiaries(UUID customerId) {
        log.info("Fetching beneficiaries for customer: {}", customerId);
        return beneficiaryRepository.findByOwnerAccountIdAndActiveTrueOrderByCreatedAtDesc(customerId)
                .stream()
                .map(this::mapToBeneficiaryResponse)
                .collect(Collectors.toList());
    }

    public BeneficiaryResponse addBeneficiary(UUID customerId, BeneficiaryRequest request) {
        log.info("Adding beneficiary {} for customer: {}", request.getBeneficiaryAccountId(), customerId);

        if (customerId.equals(request.getBeneficiaryAccountId())) {
            throw new AppException("INVALID_BENEFICIARY", "Cannot add yourself as a beneficiary");
        }

        // Check if a (possibly soft-deleted) record already exists
        java.util.Optional<Beneficiary> existing = beneficiaryRepository
                .findByOwnerAccountIdAndBeneficiaryAccountId(customerId, request.getBeneficiaryAccountId());

        if (existing.isPresent()) {
            Beneficiary b = existing.get();
            if (b.getActive()) {
                throw new AppException("BENEFICIARY_ALREADY_EXISTS", "Beneficiary already exists for this account");
            }
            // Reactivate soft-deleted entry rather than inserting a duplicate (avoids unique constraint violation)
            b.setActive(true);
            b.setNickname(request.getNickname());
            b = beneficiaryRepository.save(b);
            log.info("Beneficiary {} reactivated for customer: {}", b.getId(), customerId);
            return mapToBeneficiaryResponse(b);
        }

        Beneficiary beneficiary = Beneficiary.builder()
                .ownerAccountId(customerId)
                .beneficiaryAccountId(request.getBeneficiaryAccountId())
                .nickname(request.getNickname())
                .active(true)
                .build();

        beneficiary = beneficiaryRepository.save(beneficiary);
        log.info("Beneficiary added: {} for customer: {}", beneficiary.getId(), customerId);
        return mapToBeneficiaryResponse(beneficiary);
    }

    public void removeBeneficiary(UUID customerId, UUID beneficiaryId) {
        log.info("Removing beneficiary: {} for customer: {}", beneficiaryId, customerId);

        Beneficiary beneficiary = beneficiaryRepository.findById(beneficiaryId)
                .orElseThrow(() -> new AppException("BENEFICIARY_NOT_FOUND", "Beneficiary not found: " + beneficiaryId));

        if (!beneficiary.getOwnerAccountId().equals(customerId)) {
            throw new AppException("BENEFICIARY_NOT_FOUND", "Beneficiary not found for customer: " + customerId);
        }

        beneficiary.setActive(false);
        beneficiaryRepository.save(beneficiary);
        log.info("Beneficiary {} soft-deleted for customer: {}", beneficiaryId, customerId);
    }

    // -------------------------------------------------------------------------
    // Customer Preferences
    // -------------------------------------------------------------------------

    @Transactional(readOnly = true)
    public CustomerPreferencesResponse getPreferences(UUID customerId) {
        log.info("Fetching preferences for customer: {}", customerId);

        CustomerPreferences prefs = customerPreferencesRepository.findById(customerId)
                .orElseGet(() -> CustomerPreferences.builder()
                        .customerId(customerId)
                        .notificationEmail(true)
                        .notificationSms(false)
                        .language("en")
                        .build());

        return mapToPreferencesResponse(prefs);
    }

    public CustomerPreferencesResponse updatePreferences(UUID customerId, CustomerPreferencesRequest request) {
        log.info("Updating preferences for customer: {}", customerId);

        CustomerPreferences prefs = customerPreferencesRepository.findById(customerId)
                .orElseGet(() -> CustomerPreferences.builder()
                        .customerId(customerId)
                        .notificationEmail(true)
                        .notificationSms(false)
                        .language("en")
                        .build());

        if (request.getNotificationEmail() != null) {
            prefs.setNotificationEmail(request.getNotificationEmail());
        }
        if (request.getNotificationSms() != null) {
            prefs.setNotificationSms(request.getNotificationSms());
        }
        if (request.getLanguage() != null && !request.getLanguage().isBlank()) {
            prefs.setLanguage(request.getLanguage());
        }

        prefs = customerPreferencesRepository.save(prefs);
        log.info("Preferences updated for customer: {}", customerId);
        return mapToPreferencesResponse(prefs);
    }

    // -------------------------------------------------------------------------
    // Mappers
    // -------------------------------------------------------------------------

    private KycDocumentResponse mapToKycResponse(KycDocument doc) {
        return KycDocumentResponse.builder()
                .id(doc.getId())
                .customerId(doc.getCustomerId())
                .documentType(doc.getDocumentType())
                .documentReference(doc.getDocumentReference())
                .status(doc.getStatus())
                .rejectionReason(doc.getRejectionReason())
                .submittedAt(doc.getSubmittedAt())
                .reviewedAt(doc.getReviewedAt())
                .createdAt(doc.getCreatedAt())
                .updatedAt(doc.getUpdatedAt())
                .build();
    }

    private BeneficiaryResponse mapToBeneficiaryResponse(Beneficiary b) {
        return BeneficiaryResponse.builder()
                .id(b.getId())
                .ownerAccountId(b.getOwnerAccountId())
                .beneficiaryAccountId(b.getBeneficiaryAccountId())
                .nickname(b.getNickname())
                .active(b.getActive())
                .createdAt(b.getCreatedAt())
                .build();
    }

    private CustomerPreferencesResponse mapToPreferencesResponse(CustomerPreferences p) {
        return CustomerPreferencesResponse.builder()
                .customerId(p.getCustomerId())
                .notificationEmail(p.getNotificationEmail())
                .notificationSms(p.getNotificationSms())
                .language(p.getLanguage())
                .updatedAt(p.getUpdatedAt())
                .build();
    }
}
