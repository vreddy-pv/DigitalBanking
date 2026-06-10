package com.digitalbanking.ops.dto;

import com.digitalbanking.ops.entity.OpsCase;
import lombok.Builder;
import lombok.Data;

import java.time.OffsetDateTime;
import java.util.UUID;

@Data
@Builder
public class CaseResponse {
    private UUID id;
    private String ticketId;
    private String userId;
    private String accountId;
    private String transactionId;
    private String productLine;
    private String complaintType;
    private Integer slaDeadlineHours;
    private String caseStatus;
    private String assignedTo;
    private Integer riskScore;
    private String riskLevel;
    private String investigationSummary;
    private String flags;
    private String recommendedAction;
    private String opsNotes;
    private String outcome;
    private OffsetDateTime receivedAt;
    private OffsetDateTime updatedAt;

    public static CaseResponse from(OpsCase c) {
        return CaseResponse.builder()
                .id(c.getId())
                .ticketId(c.getTicketId())
                .userId(c.getUserId())
                .accountId(c.getAccountId())
                .transactionId(c.getTransactionId())
                .productLine(c.getProductLine())
                .complaintType(c.getComplaintType())
                .slaDeadlineHours(c.getSlaDeadlineHours())
                .caseStatus(c.getCaseStatus().name())
                .assignedTo(c.getAssignedTo())
                .riskScore(c.getRiskScore())
                .riskLevel(c.getRiskLevel())
                .investigationSummary(c.getInvestigationSummary())
                .flags(c.getFlags())
                .recommendedAction(c.getRecommendedAction())
                .opsNotes(c.getOpsNotes())
                .outcome(c.getOutcome())
                .receivedAt(c.getReceivedAt())
                .updatedAt(c.getUpdatedAt())
                .build();
    }
}
