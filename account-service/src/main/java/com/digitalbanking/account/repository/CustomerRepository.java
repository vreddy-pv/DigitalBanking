package com.digitalbanking.account.repository;

import com.digitalbanking.account.entity.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface CustomerRepository extends JpaRepository<Customer, UUID> {

    Optional<Customer> findByUserId(UUID userId);

    Optional<Customer> findByEmail(String email);

    boolean existsByUserId(UUID userId);

    boolean existsByEmail(String email);
}
