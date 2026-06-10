package com.digitalbanking.ops.repository;

import com.digitalbanking.ops.entity.OpsCase;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface OpsCaseRepository extends JpaRepository<OpsCase, UUID> {

    Optional<OpsCase> findByTicketId(String ticketId);

    boolean existsByTicketId(String ticketId);

    List<OpsCase> findAllByOrderByReceivedAtDesc();

    List<OpsCase> findByCaseStatusOrderByReceivedAtDesc(OpsCase.CaseStatus caseStatus);

    List<OpsCase> findByAssignedToOrderByReceivedAtDesc(String assignedTo);

    List<OpsCase> findByCaseStatusAndAssignedToOrderByReceivedAtDesc(
            OpsCase.CaseStatus caseStatus, String assignedTo);

    @Query("SELECT o.caseStatus, COUNT(o) FROM OpsCase o GROUP BY o.caseStatus")
    List<Object[]> countByCaseStatus();

    @Query("SELECT COUNT(o) FROM OpsCase o WHERE o.caseStatus NOT IN " +
           "(:resolved, :escalated, :rejected)")
    long countOpen(
            @Param("resolved") OpsCase.CaseStatus resolved,
            @Param("escalated") OpsCase.CaseStatus escalated,
            @Param("rejected") OpsCase.CaseStatus rejected);
}
