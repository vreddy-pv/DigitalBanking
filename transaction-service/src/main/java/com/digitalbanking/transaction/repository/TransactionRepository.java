package com.digitalbanking.transaction.repository;

import com.digitalbanking.transaction.entity.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, UUID> {

    Optional<Transaction> findByRequestId(String requestId);

    List<Transaction> findByFromAccountId(UUID fromAccountId);

    List<Transaction> findByToAccountId(UUID toAccountId);

    List<Transaction> findByFromAccountIdOrToAccountIdOrderByCreatedAtDesc(UUID fromAccountId, UUID toAccountId);
}
