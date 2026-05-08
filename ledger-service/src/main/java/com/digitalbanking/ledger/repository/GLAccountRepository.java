package com.digitalbanking.ledger.repository;

import com.digitalbanking.ledger.entity.GLAccount;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface GLAccountRepository extends JpaRepository<GLAccount, UUID> {

    Optional<GLAccount> findByCode(String code);

    Optional<GLAccount> findByName(String name);

    boolean existsByCode(String code);
}
