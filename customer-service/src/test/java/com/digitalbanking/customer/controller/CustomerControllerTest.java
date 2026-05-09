package com.digitalbanking.customer.controller;

import com.digitalbanking.customer.dto.*;
import com.digitalbanking.customer.service.CustomerService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = {CustomerController.class, HealthController.class})
@ActiveProfiles("test")
class CustomerControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private CustomerService customerService;

    // Security components needed by the filter chain
    @MockBean
    private com.digitalbanking.customer.security.JwtAuthenticationFilter jwtAuthenticationFilter;

    @MockBean
    private com.digitalbanking.customer.security.JwtTokenProvider jwtTokenProvider;

    private ObjectMapper objectMapper;
    private UUID customerId;
    private UUID docId;
    private UUID beneficiaryId;

    @BeforeEach
    void setUp() {
        objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
        customerId = UUID.randomUUID();
        docId = UUID.randomUUID();
        beneficiaryId = UUID.randomUUID();
    }

    // -------------------------------------------------------------------------
    // Health
    // -------------------------------------------------------------------------

    @Test
    void healthEndpoint_returns200() throws Exception {
        mockMvc.perform(get("/api/v1/customers/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("SERVICE_HEALTHY"));
    }

    // -------------------------------------------------------------------------
    // KYC Document endpoints
    // -------------------------------------------------------------------------

    @Test
    @WithMockUser
    void getKycDocuments_returns200WithList() throws Exception {
        KycDocumentResponse doc = KycDocumentResponse.builder()
                .id(docId)
                .customerId(customerId)
                .documentType("PASSPORT")
                .documentReference("ref-001")
                .status("PENDING")
                .createdAt(LocalDateTime.now())
                .build();

        when(customerService.getKycDocuments(customerId)).thenReturn(List.of(doc));

        mockMvc.perform(get("/api/v1/customers/{customerId}/kyc/documents", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data[0].documentType").value("PASSPORT"))
                .andExpect(jsonPath("$.data[0].status").value("PENDING"));
    }

    @Test
    @WithMockUser
    void submitKycDocument_returns201() throws Exception {
        KycDocumentRequest request = KycDocumentRequest.builder()
                .documentType("NATIONAL_ID")
                .documentReference("upload-12345")
                .build();

        KycDocumentResponse response = KycDocumentResponse.builder()
                .id(docId)
                .customerId(customerId)
                .documentType("NATIONAL_ID")
                .documentReference("upload-12345")
                .status("PENDING")
                .createdAt(LocalDateTime.now())
                .build();

        when(customerService.submitKycDocument(eq(customerId), any(KycDocumentRequest.class))).thenReturn(response);

        mockMvc.perform(post("/api/v1/customers/{customerId}/kyc/documents", customerId)
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("KYC_DOCUMENT_SUBMITTED"))
                .andExpect(jsonPath("$.data.documentType").value("NATIONAL_ID"));
    }

    @Test
    @WithMockUser
    void updateKycDocumentStatus_returns200() throws Exception {
        KycStatusUpdateRequest request = KycStatusUpdateRequest.builder()
                .status("VERIFIED")
                .build();

        KycDocumentResponse response = KycDocumentResponse.builder()
                .id(docId)
                .customerId(customerId)
                .documentType("PASSPORT")
                .documentReference("ref-001")
                .status("VERIFIED")
                .reviewedAt(LocalDateTime.now())
                .build();

        when(customerService.updateKycDocumentStatus(eq(customerId), eq(docId), any(KycStatusUpdateRequest.class)))
                .thenReturn(response);

        mockMvc.perform(put("/api/v1/customers/{customerId}/kyc/documents/{docId}/status", customerId, docId)
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.status").value("VERIFIED"));
    }

    @Test
    @WithMockUser
    void getKycStatus_returns200WithSummary() throws Exception {
        KycStatusSummaryResponse summary = KycStatusSummaryResponse.builder()
                .customerId(customerId)
                .totalDocuments(3)
                .pendingDocuments(1)
                .verifiedDocuments(2)
                .rejectedDocuments(0)
                .overallStatus("PENDING")
                .build();

        when(customerService.getKycStatus(customerId)).thenReturn(summary);

        mockMvc.perform(get("/api/v1/customers/{customerId}/kyc/status", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.totalDocuments").value(3))
                .andExpect(jsonPath("$.data.overallStatus").value("PENDING"));
    }

    // -------------------------------------------------------------------------
    // Beneficiary endpoints
    // -------------------------------------------------------------------------

    @Test
    @WithMockUser
    void getBeneficiaries_returns200WithList() throws Exception {
        UUID beneficiaryAccountId = UUID.randomUUID();
        BeneficiaryResponse b = BeneficiaryResponse.builder()
                .id(beneficiaryId)
                .ownerAccountId(customerId)
                .beneficiaryAccountId(beneficiaryAccountId)
                .nickname("John")
                .active(true)
                .createdAt(LocalDateTime.now())
                .build();

        when(customerService.getBeneficiaries(customerId)).thenReturn(List.of(b));

        mockMvc.perform(get("/api/v1/customers/{customerId}/beneficiaries", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data[0].nickname").value("John"))
                .andExpect(jsonPath("$.data[0].active").value(true));
    }

    @Test
    @WithMockUser
    void addBeneficiary_returns201() throws Exception {
        UUID beneficiaryAccountId = UUID.randomUUID();
        BeneficiaryRequest request = BeneficiaryRequest.builder()
                .beneficiaryAccountId(beneficiaryAccountId)
                .nickname("Friend's Account")
                .build();

        BeneficiaryResponse response = BeneficiaryResponse.builder()
                .id(beneficiaryId)
                .ownerAccountId(customerId)
                .beneficiaryAccountId(beneficiaryAccountId)
                .nickname("Friend's Account")
                .active(true)
                .createdAt(LocalDateTime.now())
                .build();

        when(customerService.addBeneficiary(eq(customerId), any(BeneficiaryRequest.class))).thenReturn(response);

        mockMvc.perform(post("/api/v1/customers/{customerId}/beneficiaries", customerId)
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("BENEFICIARY_ADDED"))
                .andExpect(jsonPath("$.data.nickname").value("Friend's Account"));
    }

    @Test
    @WithMockUser
    void removeBeneficiary_returns200() throws Exception {
        doNothing().when(customerService).removeBeneficiary(customerId, beneficiaryId);

        mockMvc.perform(delete("/api/v1/customers/{customerId}/beneficiaries/{beneficiaryId}",
                        customerId, beneficiaryId)
                        .with(csrf()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("BENEFICIARY_REMOVED"));
    }

    // -------------------------------------------------------------------------
    // Preferences endpoints
    // -------------------------------------------------------------------------

    @Test
    @WithMockUser
    void getPreferences_returns200() throws Exception {
        CustomerPreferencesResponse prefs = CustomerPreferencesResponse.builder()
                .customerId(customerId)
                .notificationEmail(true)
                .notificationSms(false)
                .language("en")
                .build();

        when(customerService.getPreferences(customerId)).thenReturn(prefs);

        mockMvc.perform(get("/api/v1/customers/{customerId}/preferences", customerId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.notificationEmail").value(true))
                .andExpect(jsonPath("$.data.language").value("en"));
    }

    @Test
    @WithMockUser
    void updatePreferences_returns200() throws Exception {
        CustomerPreferencesRequest request = CustomerPreferencesRequest.builder()
                .notificationSms(true)
                .language("de")
                .build();

        CustomerPreferencesResponse response = CustomerPreferencesResponse.builder()
                .customerId(customerId)
                .notificationEmail(true)
                .notificationSms(true)
                .language("de")
                .build();

        when(customerService.updatePreferences(eq(customerId), any(CustomerPreferencesRequest.class)))
                .thenReturn(response);

        mockMvc.perform(put("/api/v1/customers/{customerId}/preferences", customerId)
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.notificationSms").value(true))
                .andExpect(jsonPath("$.data.language").value("de"));
    }
}
