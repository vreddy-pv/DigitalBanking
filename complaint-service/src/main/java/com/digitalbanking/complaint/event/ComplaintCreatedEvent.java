package com.digitalbanking.complaint.event;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class ComplaintCreatedEvent {

    @Builder.Default
    private String eventType = "TransactionComplaintEvent";

    private String ticketId;
    private String userId;
    private String accountId;
    private String transactionId;
    private String productLine;
    private String complaintType;
    private int slaDeadlineHours;

    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime createdAt;
}
