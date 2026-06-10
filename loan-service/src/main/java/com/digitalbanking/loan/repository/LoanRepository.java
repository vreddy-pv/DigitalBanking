package com.digitalbanking.loan.repository;

import com.digitalbanking.loan.entity.Loan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface LoanRepository extends JpaRepository<Loan, UUID> {

    List<Loan> findByUserIdAndProductLineOrderByCreatedAtDesc(String userId, Loan.ProductLine productLine);

    List<Loan> findByUserIdOrderByCreatedAtDesc(String userId);
}
