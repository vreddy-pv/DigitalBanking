package com.digitalbanking.ledger.entity;

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
@Table(name = "journal_entries", indexes = {
    @Index(name = "idx_journal_entries_transaction_id", columnList = "transaction_id"),
    @Index(name = "idx_journal_entries_gl_account_id", columnList = "gl_account_id")
})
public class JournalEntry {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(name = "transaction_id", nullable = false)
    private UUID transactionId;

    @Column(name = "gl_account_id", nullable = false)
    private UUID glAccountId;

    @Column(precision = 15, scale = 2)
    private BigDecimal debit;

    @Column(precision = 15, scale = 2)
    private BigDecimal credit;

    @Column(name = "timestamp", nullable = false, updatable = false)
    private LocalDateTime timestamp;

    @PrePersist
    protected void onCreate() {
        timestamp = LocalDateTime.now();
    }
}
