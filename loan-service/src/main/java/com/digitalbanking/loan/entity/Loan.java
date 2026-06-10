package com.digitalbanking.loan.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.UuidGenerator;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "loans")
@Getter
@Setter
@NoArgsConstructor
public class Loan {

    @Id
    @UuidGenerator
    @Column(updatable = false, nullable = false)
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "customer_id", nullable = false)
    private String customerId;

    @Enumerated(EnumType.STRING)
    @Column(name = "product_type", nullable = false, length = 30)
    private ProductType productType;

    @Enumerated(EnumType.STRING)
    @Column(name = "product_line", nullable = false, length = 10)
    private ProductLine productLine;

    @Column(name = "disbursed_amount", nullable = false, precision = 15, scale = 2)
    private BigDecimal disbursedAmount;

    @Column(name = "outstanding_principal", nullable = false, precision = 15, scale = 2)
    private BigDecimal outstandingPrincipal;

    @Column(name = "interest_rate", nullable = false, precision = 5, scale = 2)
    private BigDecimal interestRate;

    @Column(name = "tenure_months", nullable = false)
    private Integer tenureMonths;

    @Column(name = "emi_amount", precision = 12, scale = 2)
    private BigDecimal emiAmount;

    @Column(name = "next_due_date")
    private LocalDate nextDueDate;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private LoanStatus status = LoanStatus.ACTIVE;

    @Column(nullable = false, length = 3)
    private String currency = "INR";

    @Column(name = "credit_limit", precision = 12, scale = 2)
    private BigDecimal creditLimit;

    @Column(name = "utilised_amount", precision = 12, scale = 2)
    private BigDecimal utilisedAmount;

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt;

    @OneToMany(mappedBy = "loan", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @OrderBy("dueDate ASC")
    private List<EmiSchedule> emiSchedules = new ArrayList<>();

    @PrePersist
    void onCreate() {
        createdAt = updatedAt = OffsetDateTime.now();
    }

    @PreUpdate
    void onUpdate() {
        updatedAt = OffsetDateTime.now();
    }

    public enum ProductType {
        HOME_LOAN, LAP, CONSTRUCTION_LOAN,
        PERSONAL_LOAN, CREDIT_CARD, OVERDRAFT
    }

    public enum ProductLine {
        ML, USL
    }

    public enum LoanStatus {
        ACTIVE, CLOSED, NPA, SETTLED
    }
}
