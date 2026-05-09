package com.digitalbanking.customer.repository;

import com.digitalbanking.customer.entity.KycDocument;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface KycDocumentRepository extends JpaRepository<KycDocument, UUID> {

    List<KycDocument> findByCustomerIdOrderByCreatedAtDesc(UUID customerId);

    long countByCustomerId(UUID customerId);

    long countByCustomerIdAndStatus(UUID customerId, String status);
}
