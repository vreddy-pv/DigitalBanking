package com.digitalbanking.customer.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class KycStatusSummaryResponse {

    private UUID customerId;
    private int totalDocuments;
    private int pendingDocuments;
    private int verifiedDocuments;
    private int rejectedDocuments;
    private String overallStatus;
}
