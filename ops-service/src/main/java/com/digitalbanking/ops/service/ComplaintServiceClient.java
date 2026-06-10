package com.digitalbanking.ops.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Slf4j
@Component
public class ComplaintServiceClient {

    private final RestClient restClient;

    public ComplaintServiceClient(
            @Value("${ops.complaint-service-url:http://localhost:8011}") String baseUrl) {
        this.restClient = RestClient.builder().baseUrl(baseUrl).build();
    }

    public void updateStatus(String ticketId, String status, String outcome, String opsNotes) {
        try {
            Map<String, Object> body = new java.util.HashMap<>();
            body.put("status", status);
            if (outcome != null) body.put("outcome", outcome);
            if (opsNotes != null) body.put("resolution", opsNotes);

            restClient.put()
                    .uri("/api/v1/complaints/{ticketId}/status", ticketId)
                    .body(body)
                    .retrieve()
                    .toBodilessEntity();

            log.info("Updated complaint {} to status={} outcome={}", ticketId, status, outcome);
        } catch (Exception ex) {
            log.error("Failed to update complaint {} in complaint-service: {}", ticketId, ex.getMessage());
        }
    }
}
