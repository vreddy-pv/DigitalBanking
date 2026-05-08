package com.digitalbanking.transaction.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "transactions", indexes = {
    @Index(name = "idx_transactions_from_account", columnList = "from_account_id"),
    @Index(name = "idx_transactions_to_account", columnList = "to_account_id"),
    @Index(name = "idx_transactions_created_at", columnList = "created_at")
})
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(name = "from_account_id")
    private UUID fromAccountId;

    @Column(name = "to_account_id")
    private UUID toAccountId;

    @Column(nullable = false)
    private String type;

    @Column(nullable = false, precision = 15, scale = 2)
    private BigDecimal amount;

    @Builder.Default
    @Column(nullable = false)
    private String status = "PENDING";

    private String description;

    @Column(name = "request_id", unique = true)
    private String requestId;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
