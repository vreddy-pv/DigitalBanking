package com.digitalbanking.customer.service;

import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.customer.dto.*;
import com.digitalbanking.customer.entity.Beneficiary;
import com.digitalbanking.customer.entity.CustomerPreferences;
import com.digitalbanking.customer.entity.KycDocument;
import com.digitalbanking.customer.repository.BeneficiaryRepository;
import com.digitalbanking.customer.repository.CustomerPreferencesRepository;
import com.digitalbanking.customer.repository.KycDocumentRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CustomerServiceTest {

    @Mock
    private KycDocumentRepository kycDocumentRepository;

    @Mock
    private BeneficiaryRepository beneficiaryRepository;

    @Mock
    private CustomerPreferencesRepository customerPreferencesRepository;

    @InjectMocks
    private CustomerService customerService;

    private UUID customerId;
    private UUID docId;
    private UUID beneficiaryId;

    @BeforeEach
    void setUp() {
        customerId = UUID.randomUUID();
        docId = UUID.randomUUID();
        beneficiaryId = UUID.randomUUID();
    }

    // -------------------------------------------------------------------------
    // KYC Document tests
    // -------------------------------------------------------------------------

    @Test
    void getKycDocuments_returnsListForCustomer() {
        KycDocument doc = KycDocument.builder()
                .id(docId)
                .customerId(customerId)
                .documentType("PASSPORT")
                .documentReference("S3://bucket/passport-001")
                .status("PENDING")
                .createdAt(LocalDateTime.now())
                .build();

        when(kycDocumentRepository.findByCustomerIdOrderByCreatedAtDesc(customerId))
                .thenReturn(List.of(doc));

        List<KycDocumentResponse> result = customerService.getKycDocuments(customerId);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getDocumentType()).isEqualTo("PASSPORT");
        assertThat(result.get(0).getStatus()).isEqualTo("PENDING");
        verify(kycDocumentRepository).findByCustomerIdOrderByCreatedAtDesc(customerId);
    }

    @Test
    void submitKycDocument_createsAndReturnsDocument() {
        KycDocumentRequest request = KycDocumentRequest.builder()
                .documentType("NATIONAL_ID")
                .documentReference("upload-id-12345")
                .build();

        KycDocument savedDoc = KycDocument.builder()
                .id(docId)
                .customerId(customerId)
                .documentType("NATIONAL_ID")
                .documentReference("upload-id-12345")
                .status("PENDING")
                .createdAt(LocalDateTime.now())
                .build();

        when(kycDocumentRepository.save(any(KycDocument.class))).thenReturn(savedDoc);

        KycDocumentResponse result = customerService.submitKycDocument(customerId, request);

        assertThat(result.getDocumentType()).isEqualTo("NATIONAL_ID");
        assertThat(result.getStatus()).isEqualTo("PENDING");
        assertThat(result.getCustomerId()).isEqualTo(customerId);
        verify(kycDocumentRepository).save(any(KycDocument.class));
    }

    @Test
    void updateKycDocumentStatus_verifiesDocument() {
        KycDocument doc = KycDocument.builder()
                .id(docId)
                .customerId(customerId)
                .documentType("PASSPORT")
                .documentReference("ref-001")
                .status("PENDING")
                .createdAt(LocalDateTime.now())
                .build();

        KycStatusUpdateRequest request = KycStatusUpdateRequest.builder()
                .status("VERIFIED")
                .build();

        when(kycDocumentRepository.findById(docId)).thenReturn(Optional.of(doc));
        when(kycDocumentRepository.save(any(KycDocument.class))).thenAnswer(inv -> inv.getArgument(0));

        KycDocumentResponse result = customerService.updateKycDocumentStatus(customerId, docId, request);

        assertThat(result.getStatus()).isEqualTo("VERIFIED");
        verify(kycDocumentRepository).findById(docId);
        verify(kycDocumentRepository).save(any(KycDocument.class));
    }

    @Test
    void updateKycDocumentStatus_rejectsWithReason() {
        KycDocument doc = KycDocument.builder()
                .id(docId)
                .customerId(customerId)
                .documentType("PASSPORT")
                .documentReference("ref-001")
                .status("PENDING")
                .createdAt(LocalDateTime.now())
                .build();

        KycStatusUpdateRequest request = KycStatusUpdateRequest.builder()
                .status("REJECTED")
                .rejectionReason("Document is blurry")
                .build();

        when(kycDocumentRepository.findById(docId)).thenReturn(Optional.of(doc));
        when(kycDocumentRepository.save(any(KycDocument.class))).thenAnswer(inv -> inv.getArgument(0));

        KycDocumentResponse result = customerService.updateKycDocumentStatus(customerId, docId, request);

        assertThat(result.getStatus()).isEqualTo("REJECTED");
        assertThat(result.getRejectionReason()).isEqualTo("Document is blurry");
    }

    @Test
    void updateKycDocumentStatus_throwsWhenDocumentNotFound() {
        when(kycDocumentRepository.findById(docId)).thenReturn(Optional.empty());

        KycStatusUpdateRequest request = KycStatusUpdateRequest.builder()
                .status("VERIFIED")
                .build();

        assertThatThrownBy(() -> customerService.updateKycDocumentStatus(customerId, docId, request))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("KYC document not found");
    }

    @Test
    void updateKycDocumentStatus_throwsWhenRejectedWithoutReason() {
        KycDocument doc = KycDocument.builder()
                .id(docId)
                .customerId(customerId)
                .documentType("PASSPORT")
                .documentReference("ref-001")
                .status("PENDING")
                .createdAt(LocalDateTime.now())
                .build();

        when(kycDocumentRepository.findById(docId)).thenReturn(Optional.of(doc));

        KycStatusUpdateRequest request = KycStatusUpdateRequest.builder()
                .status("REJECTED")
                .build();

        assertThatThrownBy(() -> customerService.updateKycDocumentStatus(customerId, docId, request))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("Rejection reason is required");
    }

    @Test
    void getKycStatus_returnsCorrectSummary() {
        when(kycDocumentRepository.countByCustomerId(customerId)).thenReturn(3L);
        when(kycDocumentRepository.countByCustomerIdAndStatus(customerId, "PENDING")).thenReturn(1L);
        when(kycDocumentRepository.countByCustomerIdAndStatus(customerId, "VERIFIED")).thenReturn(2L);
        when(kycDocumentRepository.countByCustomerIdAndStatus(customerId, "REJECTED")).thenReturn(0L);

        KycStatusSummaryResponse result = customerService.getKycStatus(customerId);

        assertThat(result.getTotalDocuments()).isEqualTo(3);
        assertThat(result.getPendingDocuments()).isEqualTo(1);
        assertThat(result.getVerifiedDocuments()).isEqualTo(2);
        assertThat(result.getRejectedDocuments()).isEqualTo(0);
        assertThat(result.getOverallStatus()).isEqualTo("PENDING");
    }

    @Test
    void getKycStatus_returnsVerifiedWhenAllVerified() {
        when(kycDocumentRepository.countByCustomerId(customerId)).thenReturn(2L);
        when(kycDocumentRepository.countByCustomerIdAndStatus(customerId, "PENDING")).thenReturn(0L);
        when(kycDocumentRepository.countByCustomerIdAndStatus(customerId, "VERIFIED")).thenReturn(2L);
        when(kycDocumentRepository.countByCustomerIdAndStatus(customerId, "REJECTED")).thenReturn(0L);

        KycStatusSummaryResponse result = customerService.getKycStatus(customerId);

        assertThat(result.getOverallStatus()).isEqualTo("VERIFIED");
    }

    // -------------------------------------------------------------------------
    // Beneficiary tests
    // -------------------------------------------------------------------------

    @Test
    void getBeneficiaries_returnsActiveList() {
        Beneficiary b = Beneficiary.builder()
                .id(beneficiaryId)
                .ownerAccountId(customerId)
                .beneficiaryAccountId(UUID.randomUUID())
                .nickname("John's Savings")
                .active(true)
                .createdAt(LocalDateTime.now())
                .build();

        when(beneficiaryRepository.findByOwnerAccountIdAndActiveTrueOrderByCreatedAtDesc(customerId))
                .thenReturn(List.of(b));

        List<BeneficiaryResponse> result = customerService.getBeneficiaries(customerId);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getNickname()).isEqualTo("John's Savings");
        assertThat(result.get(0).getActive()).isTrue();
    }

    @Test
    void addBeneficiary_createsSuccessfully() {
        UUID beneficiaryAccountId = UUID.randomUUID();
        BeneficiaryRequest request = BeneficiaryRequest.builder()
                .beneficiaryAccountId(beneficiaryAccountId)
                .nickname("Savings Account")
                .build();

        Beneficiary saved = Beneficiary.builder()
                .id(beneficiaryId)
                .ownerAccountId(customerId)
                .beneficiaryAccountId(beneficiaryAccountId)
                .nickname("Savings Account")
                .active(true)
                .createdAt(LocalDateTime.now())
                .build();

        when(beneficiaryRepository.findByOwnerAccountIdAndBeneficiaryAccountId(customerId, beneficiaryAccountId))
                .thenReturn(Optional.empty());
        when(beneficiaryRepository.save(any(Beneficiary.class))).thenReturn(saved);

        BeneficiaryResponse result = customerService.addBeneficiary(customerId, request);

        assertThat(result.getNickname()).isEqualTo("Savings Account");
        assertThat(result.getActive()).isTrue();
        verify(beneficiaryRepository).save(any(Beneficiary.class));
    }

    @Test
    void addBeneficiary_throwsWhenAddingSelf() {
        BeneficiaryRequest request = BeneficiaryRequest.builder()
                .beneficiaryAccountId(customerId)
                .build();

        assertThatThrownBy(() -> customerService.addBeneficiary(customerId, request))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("Cannot add yourself");
    }

    @Test
    void addBeneficiary_throwsWhenAlreadyExists() {
        UUID beneficiaryAccountId = UUID.randomUUID();
        BeneficiaryRequest request = BeneficiaryRequest.builder()
                .beneficiaryAccountId(beneficiaryAccountId)
                .build();

        Beneficiary existing = Beneficiary.builder()
                .id(beneficiaryId)
                .ownerAccountId(customerId)
                .beneficiaryAccountId(beneficiaryAccountId)
                .active(true)
                .build();

        when(beneficiaryRepository.findByOwnerAccountIdAndBeneficiaryAccountId(customerId, beneficiaryAccountId))
                .thenReturn(Optional.of(existing));

        assertThatThrownBy(() -> customerService.addBeneficiary(customerId, request))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("Beneficiary already exists");
    }

    @Test
    void removeBeneficiary_softDeletes() {
        Beneficiary b = Beneficiary.builder()
                .id(beneficiaryId)
                .ownerAccountId(customerId)
                .beneficiaryAccountId(UUID.randomUUID())
                .active(true)
                .build();

        when(beneficiaryRepository.findById(beneficiaryId)).thenReturn(Optional.of(b));
        when(beneficiaryRepository.save(any(Beneficiary.class))).thenAnswer(inv -> inv.getArgument(0));

        customerService.removeBeneficiary(customerId, beneficiaryId);

        verify(beneficiaryRepository).save(argThat(saved -> !saved.getActive()));
    }

    @Test
    void removeBeneficiary_throwsWhenNotFound() {
        when(beneficiaryRepository.findById(beneficiaryId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> customerService.removeBeneficiary(customerId, beneficiaryId))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("Beneficiary not found");
    }

    // -------------------------------------------------------------------------
    // Preferences tests
    // -------------------------------------------------------------------------

    @Test
    void getPreferences_returnsExistingPreferences() {
        CustomerPreferences prefs = CustomerPreferences.builder()
                .customerId(customerId)
                .notificationEmail(true)
                .notificationSms(false)
                .language("en")
                .build();

        when(customerPreferencesRepository.findById(customerId)).thenReturn(Optional.of(prefs));

        CustomerPreferencesResponse result = customerService.getPreferences(customerId);

        assertThat(result.getCustomerId()).isEqualTo(customerId);
        assertThat(result.getNotificationEmail()).isTrue();
        assertThat(result.getNotificationSms()).isFalse();
        assertThat(result.getLanguage()).isEqualTo("en");
    }

    @Test
    void getPreferences_returnsDefaultsWhenNotFound() {
        when(customerPreferencesRepository.findById(customerId)).thenReturn(Optional.empty());

        CustomerPreferencesResponse result = customerService.getPreferences(customerId);

        assertThat(result.getNotificationEmail()).isTrue();
        assertThat(result.getNotificationSms()).isFalse();
        assertThat(result.getLanguage()).isEqualTo("en");
    }

    @Test
    void updatePreferences_updatesSuccessfully() {
        CustomerPreferences existing = CustomerPreferences.builder()
                .customerId(customerId)
                .notificationEmail(true)
                .notificationSms(false)
                .language("en")
                .build();

        CustomerPreferencesRequest request = CustomerPreferencesRequest.builder()
                .notificationSms(true)
                .language("fr")
                .build();

        when(customerPreferencesRepository.findById(customerId)).thenReturn(Optional.of(existing));
        when(customerPreferencesRepository.save(any(CustomerPreferences.class)))
                .thenAnswer(inv -> inv.getArgument(0));

        CustomerPreferencesResponse result = customerService.updatePreferences(customerId, request);

        assertThat(result.getNotificationSms()).isTrue();
        assertThat(result.getLanguage()).isEqualTo("fr");
        assertThat(result.getNotificationEmail()).isTrue();
    }
}
