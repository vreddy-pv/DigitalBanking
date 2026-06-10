package com.digitalbanking.ops.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.UuidGenerator;

import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "ops_cases")
@Getter
@Setter
@NoArgsConstructor
public class OpsCase {

    @Id
    @UuidGenerator
    @Column(updatable = false, nullable = false)
    private UUID id;

    @Column(name = "ticket_id", nullable = false, unique = true, length = 50)
    private String ticketId;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "account_id")
    private String accountId;

    @Column(name = "transaction_id")
    private String transactionId;

    @Column(name = "product_line", length = 10)
    private String productLine;

    @Column(name = "complaint_type", length = 20)
    private String complaintType;

    @Column(name = "sla_deadline_hours")
    private Integer slaDeadlineHours;

    @Enumerated(EnumType.STRING)
    @Column(name = "case_status", nullable = false, length = 25)
    private CaseStatus caseStatus = CaseStatus.OPEN;

    @Column(name = "assigned_to")
    private String assignedTo;

    @Column(name = "risk_score")
    private Integer riskScore;

    @Column(name = "risk_level", length = 10)
    private String riskLevel;

    @Column(name = "investigation_summary", columnDefinition = "TEXT")
    private String investigationSummary;

    @Column(name = "flags", columnDefinition = "TEXT")
    private String flags;

    @Column(name = "recommended_action", length = 30)
    private String recommendedAction;

    @Column(name = "ops_notes", columnDefinition = "TEXT")
    private String opsNotes;

    @Column(name = "outcome", length = 20)
    private String outcome;

    @Column(name = "received_at", nullable = false)
    private OffsetDateTime receivedAt;

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt;

    @PrePersist
    void onCreate() {
        receivedAt = updatedAt = OffsetDateTime.now();
    }

    @PreUpdate
    void onUpdate() {
        updatedAt = OffsetDateTime.now();
    }

    public enum CaseStatus {
        OPEN, UNDER_INVESTIGATION, AWAITING_REVIEW, RESOLVED, ESCALATED, REJECTED
    }
}
