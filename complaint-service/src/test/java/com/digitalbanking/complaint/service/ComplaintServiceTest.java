package com.digitalbanking.complaint.service;

import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.complaint.dto.CreateComplaintRequest;
import com.digitalbanking.complaint.dto.ComplaintResponse;
import com.digitalbanking.complaint.dto.UpdateStatusRequest;
import com.digitalbanking.complaint.entity.Complaint;
import com.digitalbanking.complaint.event.ComplaintEventPublisher;
import com.digitalbanking.complaint.repository.ComplaintRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ComplaintServiceTest {

    @Mock
    private ComplaintRepository complaintRepository;

    @Mock
    private ComplaintEventPublisher eventPublisher;

    @InjectMocks
    private ComplaintService complaintService;

    private CreateComplaintRequest validRequest;

    @BeforeEach
    void setUp() {
        validRequest = new CreateComplaintRequest();
        validRequest.setUserId("user-123");
        validRequest.setAccountId("acc-456");
        validRequest.setTransactionId("txn-789");
        validRequest.setProductLine("CASA");
        validRequest.setComplaintType("UNAUTHORIZED");
        validRequest.setDescription("I did not make this transaction at XYZ Merchant.");
    }

    @Test
    void createComplaint_savesEntityAndPublishesEvent() {
        when(complaintRepository.existsByTicketId(anyString())).thenReturn(false);
        when(complaintRepository.save(any(Complaint.class))).thenAnswer(inv -> {
            Complaint c = inv.getArgument(0);
            c.onCreate();
            return c;
        });

        ComplaintResponse response = complaintService.createComplaint(validRequest);

        assertThat(response.getTicketId()).startsWith("CMP-");
        assertThat(response.getStatus()).isEqualTo("ACCEPTED");
        assertThat(response.getUserId()).isEqualTo("user-123");
        assertThat(response.getComplaintType()).isEqualTo("UNAUTHORIZED");
        assertThat(response.getSlaDeadline()).isAfter(LocalDateTime.now());
        verify(eventPublisher).publish(argThat(e -> e.getTicketId().equals(response.getTicketId())));
    }

    @Test
    void createComplaint_fraudTypeSets4HourSla() {
        validRequest.setComplaintType("FRAUD");
        when(complaintRepository.existsByTicketId(anyString())).thenReturn(false);
        when(complaintRepository.save(any(Complaint.class))).thenAnswer(inv -> {
            Complaint c = inv.getArgument(0);
            c.onCreate();
            return c;
        });

        ComplaintResponse response = complaintService.createComplaint(validRequest);

        // SLA deadline should be ~4 hours from now
        assertThat(response.getSlaDeadline())
                .isBetween(LocalDateTime.now().plusHours(3), LocalDateTime.now().plusHours(5));
    }

    @Test
    void createComplaint_errorTypeSets48HourSla() {
        validRequest.setComplaintType("ERROR");
        when(complaintRepository.existsByTicketId(anyString())).thenReturn(false);
        when(complaintRepository.save(any(Complaint.class))).thenAnswer(inv -> {
            Complaint c = inv.getArgument(0);
            c.onCreate();
            return c;
        });

        ComplaintResponse response = complaintService.createComplaint(validRequest);

        assertThat(response.getSlaDeadline())
                .isBetween(LocalDateTime.now().plusHours(47), LocalDateTime.now().plusHours(49));
    }

    @Test
    void getByTicketId_returnsComplaintForOwner() {
        Complaint c = buildSavedComplaint("CMP-20260611-ABCDEF", "user-123");
        when(complaintRepository.findByTicketId("CMP-20260611-ABCDEF")).thenReturn(Optional.of(c));

        ComplaintResponse response = complaintService.getByTicketId("CMP-20260611-ABCDEF", "user-123");

        assertThat(response.getTicketId()).isEqualTo("CMP-20260611-ABCDEF");
    }

    @Test
    void getByTicketId_throwsForbiddenForWrongUser() {
        Complaint c = buildSavedComplaint("CMP-20260611-ABCDEF", "user-123");
        when(complaintRepository.findByTicketId("CMP-20260611-ABCDEF")).thenReturn(Optional.of(c));

        assertThatThrownBy(() ->
                complaintService.getByTicketId("CMP-20260611-ABCDEF", "other-user"))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("authorised");
    }

    @Test
    void getByTicketId_throwsNotFoundForMissingTicket() {
        when(complaintRepository.findByTicketId(anyString())).thenReturn(Optional.empty());

        assertThatThrownBy(() ->
                complaintService.getByTicketId("CMP-MISSING", "user-123"))
                .isInstanceOf(AppException.class)
                .hasMessageContaining("not found");
    }

    @Test
    void getByUserId_returnsAllComplaintsForUser() {
        List<Complaint> complaints = List.of(
                buildSavedComplaint("CMP-1", "user-123"),
                buildSavedComplaint("CMP-2", "user-123")
        );
        when(complaintRepository.findByUserIdOrderByCreatedAtDesc("user-123")).thenReturn(complaints);

        List<ComplaintResponse> result = complaintService.getByUserId("user-123");

        assertThat(result).hasSize(2);
    }

    @Test
    void updateStatus_changesStatusOnComplaint() {
        Complaint c = buildSavedComplaint("CMP-20260611-ABCDEF", "user-123");
        when(complaintRepository.findByTicketId("CMP-20260611-ABCDEF")).thenReturn(Optional.of(c));
        when(complaintRepository.save(any(Complaint.class))).thenAnswer(inv -> inv.getArgument(0));

        UpdateStatusRequest req = new UpdateStatusRequest();
        req.setStatus("UNDER_INVESTIGATION");
        req.setOpsAnalystId("analyst-001");

        ComplaintResponse response = complaintService.updateStatus("CMP-20260611-ABCDEF", req);

        assertThat(response.getStatus()).isEqualTo("UNDER_INVESTIGATION");
        assertThat(response.getOpsAnalystId()).isEqualTo("analyst-001");
    }

    // ── Helpers ─────────────────────────────────────────────────────────────

    private Complaint buildSavedComplaint(String ticketId, String userId) {
        Complaint c = Complaint.builder()
                .id(UUID.randomUUID())
                .ticketId(ticketId)
                .userId(userId)
                .accountId("acc-456")
                .transactionId("txn-789")
                .productLine("CASA")
                .complaintType("UNAUTHORIZED")
                .description("Test description for complaint.")
                .status("ACCEPTED")
                .slaDeadline(LocalDateTime.now().plusHours(4))
                .build();
        c.onCreate();
        return c;
    }
}
