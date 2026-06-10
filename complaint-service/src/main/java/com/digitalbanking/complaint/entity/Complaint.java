package com.digitalbanking.complaint.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.UuidGenerator;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "complaints")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Complaint {

    @Id
    @UuidGenerator
    @Column(nullable = false, updatable = false)
    private UUID id;

    @Column(name = "ticket_id", nullable = false, unique = true, length = 30)
    private String ticketId;

    @Column(name = "user_id", nullable = false, length = 36)
    private String userId;

    @Column(name = "account_id", nullable = false, length = 36)
    private String accountId;

    @Column(name = "transaction_id", length = 36)
    private String transactionId;

    @Column(name = "product_line", nullable = false, length = 10)
    private String productLine;

    @Column(name = "complaint_type", nullable = false, length = 20)
    private String complaintType;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false, length = 20)
    @Builder.Default
    private String status = "ACCEPTED";

    @Column(name = "ops_analyst_id", length = 36)
    private String opsAnalystId;

    @Column(columnDefinition = "TEXT")
    private String resolution;

    @Column(length = 20)
    private String outcome;

    @Column(name = "sla_deadline")
    private LocalDateTime slaDeadline;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    void onCreate() {
        LocalDateTime now = LocalDateTime.now();
        createdAt = now;
        updatedAt = now;
    }

    @PreUpdate
    void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
