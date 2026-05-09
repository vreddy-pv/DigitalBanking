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
@Table(name = "customer_preferences")
public class CustomerPreferences {

    @Id
    @Column(name = "customer_id")
    private UUID customerId;

    @Builder.Default
    @Column(name = "notification_email")
    private Boolean notificationEmail = true;

    @Builder.Default
    @Column(name = "notification_sms")
    private Boolean notificationSms = false;

    @Builder.Default
    @Column(name = "language", length = 10)
    private String language = "en";

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
