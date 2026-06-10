package com.digitalbanking.ops.controller;

import com.digitalbanking.ops.dto.AssignCaseRequest;
import com.digitalbanking.ops.dto.ResolveCaseRequest;
import com.digitalbanking.ops.entity.OpsCase;
import com.digitalbanking.ops.repository.OpsCaseRepository;
import com.digitalbanking.ops.service.ComplaintServiceClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.time.OffsetDateTime;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class OpsControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("ops_db")
            .withUsername("postgres")
            .withPassword("password");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.autoconfigure.exclude",
                () -> "org.springframework.boot.autoconfigure.amqp.RabbitAutoConfiguration");
    }

    @MockitoBean
    private ComplaintServiceClient complaintServiceClient;

    @Autowired private MockMvc mockMvc;
    @Autowired private OpsCaseRepository repository;
    @Autowired private ObjectMapper objectMapper;

    @BeforeEach
    void cleanUp() {
        repository.deleteAll();
    }

    @Test
    void health_returns200() throws Exception {
        mockMvc.perform(get("/api/v1/ops/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").value("UP"));
    }

    @Test
    void listCases_returnsAll() throws Exception {
        saveCase("CMP-IT-001", OpsCase.CaseStatus.OPEN);
        saveCase("CMP-IT-002", OpsCase.CaseStatus.AWAITING_REVIEW);

        mockMvc.perform(get("/api/v1/ops/cases"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(2)));
    }

    @Test
    void listCases_filterByStatus_returnsFiltered() throws Exception {
        saveCase("CMP-IT-003", OpsCase.CaseStatus.OPEN);
        saveCase("CMP-IT-004", OpsCase.CaseStatus.RESOLVED);

        mockMvc.perform(get("/api/v1/ops/cases").param("status", "OPEN"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].ticketId").value("CMP-IT-003"));
    }

    @Test
    void getCase_returnsCase() throws Exception {
        saveCase("CMP-IT-005", OpsCase.CaseStatus.OPEN);

        mockMvc.perform(get("/api/v1/ops/cases/{ticketId}", "CMP-IT-005"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.ticketId").value("CMP-IT-005"))
                .andExpect(jsonPath("$.data.caseStatus").value("OPEN"));
    }

    @Test
    void getCase_notFound_returns404() throws Exception {
        mockMvc.perform(get("/api/v1/ops/cases/{ticketId}", "NO-SUCH-TICKET"))
                .andExpect(status().isNotFound());
    }

    @Test
    void assignCase_assignsAndChangesStatus() throws Exception {
        saveCase("CMP-IT-006", OpsCase.CaseStatus.OPEN);

        AssignCaseRequest req = new AssignCaseRequest();
        req.setAnalystId("analyst-99");

        mockMvc.perform(put("/api/v1/ops/cases/{ticketId}/assign", "CMP-IT-006")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.assignedTo").value("analyst-99"))
                .andExpect(jsonPath("$.data.caseStatus").value("AWAITING_REVIEW"));
    }

    @Test
    void resolveCase_setsOutcomeAndCallsComplaintService() throws Exception {
        saveCase("CMP-IT-007", OpsCase.CaseStatus.AWAITING_REVIEW);

        ResolveCaseRequest req = new ResolveCaseRequest();
        req.setOutcome("RESOLVED");
        req.setOpsNotes("Genuine customer transaction confirmed.");

        mockMvc.perform(put("/api/v1/ops/cases/{ticketId}/resolve", "CMP-IT-007")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.caseStatus").value("RESOLVED"))
                .andExpect(jsonPath("$.data.outcome").value("RESOLVED"));
    }

    @Test
    void resolveCase_invalidOutcome_returns400() throws Exception {
        saveCase("CMP-IT-008", OpsCase.CaseStatus.AWAITING_REVIEW);

        ResolveCaseRequest req = new ResolveCaseRequest();
        req.setOutcome("INVALID_OUTCOME");

        mockMvc.perform(put("/api/v1/ops/cases/{ticketId}/resolve", "CMP-IT-008")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void getStats_returnsCounts() throws Exception {
        saveCase("CMP-IT-009", OpsCase.CaseStatus.OPEN);
        saveCase("CMP-IT-010", OpsCase.CaseStatus.AWAITING_REVIEW);
        saveCase("CMP-IT-011", OpsCase.CaseStatus.RESOLVED);

        mockMvc.perform(get("/api/v1/ops/stats"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.open").value(1))
                .andExpect(jsonPath("$.data.awaitingReview").value(1))
                .andExpect(jsonPath("$.data.resolved").value(1))
                .andExpect(jsonPath("$.data.totalActive").value(2));
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private OpsCase saveCase(String ticketId, OpsCase.CaseStatus status) {
        OpsCase c = new OpsCase();
        c.setTicketId(ticketId);
        c.setUserId("user-it-test");
        c.setComplaintType("UNAUTHORIZED");
        c.setProductLine("CASA");
        c.setCaseStatus(status);
        c.setReceivedAt(OffsetDateTime.now());
        c.setUpdatedAt(OffsetDateTime.now());
        return repository.save(c);
    }
}
