package com.digitalbanking.customer.repository;

import com.digitalbanking.customer.entity.Beneficiary;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface BeneficiaryRepository extends JpaRepository<Beneficiary, UUID> {

    List<Beneficiary> findByOwnerAccountIdAndActiveTrueOrderByCreatedAtDesc(UUID ownerAccountId);

    Optional<Beneficiary> findByOwnerAccountIdAndBeneficiaryAccountId(UUID ownerAccountId, UUID beneficiaryAccountId);
}
