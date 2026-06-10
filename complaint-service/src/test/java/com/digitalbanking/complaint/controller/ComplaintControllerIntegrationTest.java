package com.digitalbanking.complaint.controller;

import com.digitalbanking.complaint.dto.CreateComplaintRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
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

import com.digitalbanking.complaint.event.ComplaintEventPublisher;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doNothing;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class ComplaintControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("complaint_db")
            .withUsername("postgres")
            .withPassword("password");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        // Disable RabbitMQ auto-config for tests
        registry.add("spring.autoconfigure.exclude",
                () -> "org.springframework.boot.autoconfigure.amqp.RabbitAutoConfiguration");
    }

    @MockitoBean
    private ComplaintEventPublisher eventPublisher;

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void health_returns200() throws Exception {
        mockMvc.perform(get("/api/v1/complaints/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").value("UP"));
    }

    @Test
    void createComplaint_returns201WithTicketId() throws Exception {
        doNothing().when(eventPublisher).publish(any());

        CreateComplaintRequest req = buildRequest("UNAUTHORIZED");
        mockMvc.perform(post("/api/v1/complaints")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.ticketId").value(org.hamcrest.Matchers.startsWith("CMP-")))
                .andExpect(jsonPath("$.data.status").value("ACCEPTED"))
                .andExpect(jsonPath("$.data.userId").value("user-integration-test"));
    }

    @Test
    void createComplaint_invalidRequest_returns400() throws Exception {
        CreateComplaintRequest req = new CreateComplaintRequest();
        req.setUserId("user-123");
        // Missing required fields

        mockMvc.perform(post("/api/v1/complaints")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void getComplaint_byTicketId_returnsComplaint() throws Exception {
        doNothing().when(eventPublisher).publish(any());

        // Create first
        CreateComplaintRequest req = buildRequest("DISPUTE");
        String createBody = mockMvc.perform(post("/api/v1/complaints")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();

        String ticketId = objectMapper.readTree(createBody).at("/data/ticketId").asText();

        // Retrieve
        mockMvc.perform(get("/api/v1/complaints/{ticketId}", ticketId)
                        .param("userId", "user-integration-test"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.ticketId").value(ticketId));
    }

    @Test
    void getComplaint_wrongUser_returns403() throws Exception {
        doNothing().when(eventPublisher).publish(any());

        CreateComplaintRequest req = buildRequest("FRAUD");
        String createBody = mockMvc.perform(post("/api/v1/complaints")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();

        String ticketId = objectMapper.readTree(createBody).at("/data/ticketId").asText();

        mockMvc.perform(get("/api/v1/complaints/{ticketId}", ticketId)
                        .param("userId", "different-user"))
                .andExpect(status().isForbidden());
    }

    @Test
    void getUserComplaints_returnsListForUser() throws Exception {
        doNothing().when(eventPublisher).publish(any());
        String userId = "user-list-test-" + System.currentTimeMillis();

        CreateComplaintRequest req = buildRequest("ERROR");
        req.setUserId(userId);
        mockMvc.perform(post("/api/v1/complaints")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(req)));

        mockMvc.perform(get("/api/v1/complaints/user/{userId}", userId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data.length()").value(1));
    }

    // ── helpers ──────────────────────────────────────────────────────────────

    private CreateComplaintRequest buildRequest(String complaintType) {
        CreateComplaintRequest req = new CreateComplaintRequest();
        req.setUserId("user-integration-test");
        req.setAccountId("acc-uuid-integration");
        req.setTransactionId("txn-uuid-integration");
        req.setProductLine("CASA");
        req.setComplaintType(complaintType);
        req.setDescription("Integration test complaint for type " + complaintType + ".");
        return req;
    }
}
