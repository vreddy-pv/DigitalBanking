package com.digitalbanking.complaint.dto;

import com.digitalbanking.complaint.entity.Complaint;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class ComplaintResponse {

    private String ticketId;
    private String userId;
    private String accountId;
    private String transactionId;
    private String productLine;
    private String complaintType;
    private String description;
    private String status;
    private String opsAnalystId;
    private String resolution;
    private String outcome;
    private LocalDateTime slaDeadline;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public static ComplaintResponse from(Complaint c) {
        return ComplaintResponse.builder()
                .ticketId(c.getTicketId())
                .userId(c.getUserId())
                .accountId(c.getAccountId())
                .transactionId(c.getTransactionId())
                .productLine(c.getProductLine())
                .complaintType(c.getComplaintType())
                .description(c.getDescription())
                .status(c.getStatus())
                .opsAnalystId(c.getOpsAnalystId())
                .resolution(c.getResolution())
                .outcome(c.getOutcome())
                .slaDeadline(c.getSlaDeadline())
                .createdAt(c.getCreatedAt())
                .updatedAt(c.getUpdatedAt())
                .build();
    }
}
