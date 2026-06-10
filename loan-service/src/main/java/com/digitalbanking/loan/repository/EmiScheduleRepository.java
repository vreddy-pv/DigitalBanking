package com.digitalbanking.loan.repository;

import com.digitalbanking.loan.entity.EmiSchedule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@Repository
public interface EmiScheduleRepository extends JpaRepository<EmiSchedule, UUID> {

    List<EmiSchedule> findByLoanIdAndDueDateGreaterThanEqualOrderByDueDateAsc(UUID loanId, LocalDate from);
}
