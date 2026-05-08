package com.digitalbanking.ledger.repository;

import com.digitalbanking.ledger.entity.JournalEntry;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface JournalEntryRepository extends JpaRepository<JournalEntry, UUID> {

    List<JournalEntry> findByTransactionId(UUID transactionId);

    List<JournalEntry> findByGlAccountIdOrderByTimestampDesc(UUID glAccountId);
}
