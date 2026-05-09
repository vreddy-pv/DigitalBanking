package com.digitalbanking.customer.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "beneficiaries", indexes = {
    @Index(name = "idx_beneficiaries_owner", columnList = "owner_account_id"),
    @Index(name = "idx_beneficiaries_active", columnList = "active")
},
uniqueConstraints = {
    @UniqueConstraint(name = "uq_beneficiaries_owner_beneficiary",
            columnNames = {"owner_account_id", "beneficiary_account_id"})
})
public class Beneficiary {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(name = "owner_account_id", nullable = false)
    private UUID ownerAccountId;

    @Column(name = "beneficiary_account_id", nullable = false)
    private UUID beneficiaryAccountId;

    @Column(name = "nickname", length = 100)
    private String nickname;

    @Builder.Default
    @Column(name = "active")
    private Boolean active = true;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
