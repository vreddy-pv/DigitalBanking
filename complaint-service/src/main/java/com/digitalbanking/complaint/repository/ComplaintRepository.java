package com.digitalbanking.complaint.repository;

import com.digitalbanking.complaint.entity.Complaint;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ComplaintRepository extends JpaRepository<Complaint, UUID> {

    Optional<Complaint> findByTicketId(String ticketId);

    List<Complaint> findByUserIdOrderByCreatedAtDesc(String userId);

    boolean existsByTicketId(String ticketId);
}
