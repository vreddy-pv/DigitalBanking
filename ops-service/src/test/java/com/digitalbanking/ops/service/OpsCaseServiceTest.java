package com.digitalbanking.ops.service;

import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.ops.dto.AssignCaseRequest;
import com.digitalbanking.ops.dto.CaseResponse;
import com.digitalbanking.ops.dto.OpsStatsResponse;
import com.digitalbanking.ops.dto.ResolveCaseRequest;
import com.digitalbanking.ops.entity.OpsCase;
import com.digitalbanking.ops.repository.OpsCaseRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.OffsetDateTime;
import java.util.*;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OpsCaseServiceTest {

    @Mock private OpsCaseRepository repository;
    @Mock private ComplaintServiceClient complaintClient;
    @InjectMocks private OpsCaseService service;

    @Test
    void createCase_savesNewCase() {
        when(repository.existsByTicketId("CMP-001")).thenReturn(false);
        when(repository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        service.createCase(buildCreatedEvent("CMP-001", "CASA", "UNAUTHORIZED"));

        verify(repository).save(argThat(c -> "CMP-001".equals(c.getTicketId())
                && "UNAUTHORIZED".equals(c.getComplaintType())
                && c.getCaseStatus() == OpsCase.CaseStatus.OPEN));
    }

    @Test
    void createCase_duplicateTicketId_skips() {
        when(repository.existsByTicketId("CMP-001")).thenReturn(true);

        service.createCase(buildCreatedEvent("CMP-001", "CASA", "FRAUD"));

        verify(repository, never()).save(any());
    }

    @Test
    void updateWithInvestigation_manualReview_setsAwaitingReview() {
        OpsCase opsCase = buildOpsCase("CMP-002", OpsCase.CaseStatus.OPEN);
        when(repository.findByTicketId("CMP-002")).thenReturn(Optional.of(opsCase));
        when(repository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        service.updateWithInvestigation(buildInvestigatedEvent("CMP-002", 55, "HIGH", "MANUAL_REVIEW"));

        verify(repository).save(argThat(c ->
                c.getCaseStatus() == OpsCase.CaseStatus.AWAITING_REVIEW
                && c.getRiskScore() == 55
                && "HIGH".equals(c.getRiskLevel())));
    }

    @Test
    void updateWithInvestigation_autoResolve_setsResolved() {
        OpsCase opsCase = buildOpsCase("CMP-003", OpsCase.CaseStatus.OPEN);
        when(repository.findByTicketId("CMP-003")).thenReturn(Optional.of(opsCase));
        when(repository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        service.updateWithInvestigation(buildInvestigatedEvent("CMP-003", 10, "LOW", "AUTO_RESOLVE"));

        verify(repository).save(argThat(c ->
                c.getCaseStatus() == OpsCase.CaseStatus.RESOLVED
                && "RESOLVED".equals(c.getOutcome())));
    }

    @Test
    void updateWithInvestigation_escalateFraud_setsEscalated() {
        OpsCase opsCase = buildOpsCase("CMP-004", OpsCase.CaseStatus.OPEN);
        when(repository.findByTicketId("CMP-004")).thenReturn(Optional.of(opsCase));
        when(repository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        service.updateWithInvestigation(buildInvestigatedEvent("CMP-004", 85, "CRITICAL", "ESCALATE_FRAUD"));

        verify(repository).save(argThat(c ->
                c.getCaseStatus() == OpsCase.CaseStatus.ESCALATED
                && "ESCALATED".equals(c.getOutcome())));
    }

    @Test
    void assignCase_openCase_assignsAndMovesToAwaitingReview() {
        OpsCase opsCase = buildOpsCase("CMP-005", OpsCase.CaseStatus.OPEN);
        when(repository.findByTicketId("CMP-005")).thenReturn(Optional.of(opsCase));
        when(repository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        AssignCaseRequest req = new AssignCaseRequest();
        req.setAnalystId("analyst-01");
        CaseResponse result = service.assignCase("CMP-005", req);

        assertThat(result.getAssignedTo()).isEqualTo("analyst-01");
        assertThat(result.getCaseStatus()).isEqualTo("AWAITING_REVIEW");
    }

    @Test
    void assignCase_closedCase_throwsException() {
        OpsCase opsCase = buildOpsCase("CMP-006", OpsCase.CaseStatus.RESOLVED);
        when(repository.findByTicketId("CMP-006")).thenReturn(Optional.of(opsCase));

        AssignCaseRequest req = new AssignCaseRequest();
        req.setAnalystId("analyst-01");

        assertThatThrownBy(() -> service.assignCase("CMP-006", req))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("already RESOLVED");
    }

    @Test
    void resolveCase_updatesStatusAndCallsComplaintService() {
        OpsCase opsCase = buildOpsCase("CMP-007", OpsCase.CaseStatus.AWAITING_REVIEW);
        when(repository.findByTicketId("CMP-007")).thenReturn(Optional.of(opsCase));
        when(repository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        ResolveCaseRequest req = new ResolveCaseRequest();
        req.setOutcome("RESOLVED");
        req.setOpsNotes("Verified genuine transaction.");
        CaseResponse result = service.resolveCase("CMP-007", req);

        assertThat(result.getCaseStatus()).isEqualTo("RESOLVED");
        assertThat(result.getOutcome()).isEqualTo("RESOLVED");
        verify(complaintClient).updateStatus("CMP-007", "RESOLVED", "RESOLVED", "Verified genuine transaction.");
    }

    @Test
    void getStats_returnsAggregatedCounts() {
        List<Object[]> rows = List.of(
                new Object[]{OpsCase.CaseStatus.OPEN, 5L},
                new Object[]{OpsCase.CaseStatus.AWAITING_REVIEW, 3L},
                new Object[]{OpsCase.CaseStatus.RESOLVED, 10L}
        );
        when(repository.countByCaseStatus()).thenReturn(rows);

        OpsStatsResponse stats = service.getStats();

        assertThat(stats.getOpen()).isEqualTo(5L);
        assertThat(stats.getAwaitingReview()).isEqualTo(3L);
        assertThat(stats.getResolved()).isEqualTo(10L);
        assertThat(stats.getTotalActive()).isEqualTo(8L);
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private Map<String, Object> buildCreatedEvent(String ticketId, String productLine, String complaintType) {
        Map<String, Object> event = new HashMap<>();
        event.put("ticketId", ticketId);
        event.put("userId", "user-test");
        event.put("accountId", "acc-test");
        event.put("transactionId", "txn-test");
        event.put("productLine", productLine);
        event.put("complaintType", complaintType);
        event.put("slaDeadlineHours", 4);
        return event;
    }

    private Map<String, Object> buildInvestigatedEvent(
            String ticketId, int riskScore, String riskLevel, String action) {
        Map<String, Object> event = new HashMap<>();
        event.put("ticketId", ticketId);
        event.put("riskScore", riskScore);
        event.put("riskLevel", riskLevel);
        event.put("summary", "Test investigation summary.");
        event.put("recommendedAction", action);
        event.put("flags", List.of("VELOCITY_ANOMALY").toString());
        return event;
    }

    private OpsCase buildOpsCase(String ticketId, OpsCase.CaseStatus status) {
        OpsCase c = new OpsCase();
        c.setId(UUID.randomUUID());
        c.setTicketId(ticketId);
        c.setUserId("user-test");
        c.setComplaintType("UNAUTHORIZED");
        c.setProductLine("CASA");
        c.setCaseStatus(status);
        c.setReceivedAt(OffsetDateTime.now());
        c.setUpdatedAt(OffsetDateTime.now());
        return c;
    }
}
