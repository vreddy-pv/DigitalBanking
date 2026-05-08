package com.digitalbanking.account.controller;

import com.digitalbanking.account.dto.CustomerRegistrationRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.time.LocalDate;
import java.util.UUID;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
public class AccountControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("account_db")
            .withUsername("postgres")
            .withPassword("password");

    @DynamicPropertySource
    static void registerDynamicProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void testRegisterCustomer_Success() throws Exception {
        CustomerRegistrationRequest request = CustomerRegistrationRequest.builder()
                .userId(UUID.randomUUID().toString())
                .name("John Doe")
                .dob(LocalDate.of(1990, 1, 1))
                .email("john@example.com")
                .phone("1234567890")
                .addressLine1("123 Main St")
                .city("New York")
                .state("NY")
                .zipCode("10001")
                .country("USA")
                .pan("ABCDE1234F")
                .aadhar("123456789012")
                .accountType("SAVINGS")
                .build();

        mockMvc.perform(post("/api/v1/accounts/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("CUSTOMER_REGISTERED"))
                .andExpect(jsonPath("$.data.name").value("John Doe"))
                .andExpect(jsonPath("$.data.email").value("john@example.com"));
    }

    @Test
    void testRegisterCustomer_InvalidEmail() throws Exception {
        CustomerRegistrationRequest request = CustomerRegistrationRequest.builder()
                .userId(UUID.randomUUID().toString())
                .name("John Doe")
                .dob(LocalDate.of(1990, 1, 1))
                .email("invalid-email")
                .accountType("SAVINGS")
                .build();

        mockMvc.perform(post("/api/v1/accounts/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false));
    }

    @Test
    void testRegisterCustomer_MissingName() throws Exception {
        CustomerRegistrationRequest request = CustomerRegistrationRequest.builder()
                .userId(UUID.randomUUID().toString())
                .name("")
                .dob(LocalDate.of(1990, 1, 1))
                .email("john@example.com")
                .accountType("SAVINGS")
                .build();

        mockMvc.perform(post("/api/v1/accounts/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false));
    }

    @Test
    void testHealthCheck() throws Exception {
        mockMvc.perform(get("/api/v1/accounts/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("SERVICE_HEALTHY"))
                .andExpect(jsonPath("$.data").value("UP"));
    }
}
