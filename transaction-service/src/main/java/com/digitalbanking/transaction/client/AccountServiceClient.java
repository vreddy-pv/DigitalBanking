package com.digitalbanking.transaction.client;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Optional;
import java.util.UUID;

@Slf4j
@Component
public class AccountServiceClient {

    private final RestTemplate restTemplate;
    private final String accountServiceUrl;

    public AccountServiceClient(
            RestTemplate restTemplate,
            @Value("${services.account-service.url:http://account-service:8002}") String accountServiceUrl) {
        this.restTemplate = restTemplate;
        this.accountServiceUrl = accountServiceUrl;
    }

    public Optional<AccountData> getAccountById(UUID accountId) {
        String url = accountServiceUrl + "/api/v1/accounts/" + accountId;
        try {
            AccountResponse response = restTemplate.getForObject(url, AccountResponse.class);
            if (response != null && response.success() && response.data() != null) {
                return Optional.of(response.data());
            }
            log.warn("Account service returned no data for accountId={}", accountId);
            return Optional.empty();
        } catch (Exception e) {
            log.warn("Failed to fetch account data for accountId={}: {}", accountId, e.getMessage());
            return Optional.empty();
        }
    }

    public Optional<CustomerData> getCustomerById(UUID customerId) {
        String url = accountServiceUrl + "/api/v1/accounts/customer/" + customerId;
        try {
            CustomerResponse response = restTemplate.getForObject(url, CustomerResponse.class);
            if (response != null && response.success() && response.data() != null) {
                return Optional.of(response.data());
            }
            log.warn("Account service returned no customer data for customerId={}", customerId);
            return Optional.empty();
        } catch (Exception e) {
            log.warn("Failed to fetch customer data for customerId={}: {}", customerId, e.getMessage());
            return Optional.empty();
        }
    }

    // DTO records

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record AccountData(UUID id, UUID customerId, String accountNumber) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record CustomerData(UUID id, String name, String email) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    private record AccountResponse(boolean success, AccountData data) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    private record CustomerResponse(boolean success, CustomerData data) {}
}
