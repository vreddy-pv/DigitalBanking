package com.digitalbanking.complaint.service;

import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.complaint.dto.CreateComplaintRequest;
import com.digitalbanking.complaint.dto.ComplaintResponse;
import com.digitalbanking.complaint.dto.UpdateStatusRequest;
import com.digitalbanking.complaint.entity.Complaint;
import com.digitalbanking.complaint.event.ComplaintCreatedEvent;
import com.digitalbanking.complaint.event.ComplaintEventPublisher;
import com.digitalbanking.complaint.repository.ComplaintRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class ComplaintService {

    private static final Map<String, Integer> SLA_HOURS = Map.of(
            "FRAUD",         4,
            "UNAUTHORIZED",  4,
            "DISPUTE",       24,
            "ERROR",         48
    );

    private final ComplaintRepository complaintRepository;
    private final ComplaintEventPublisher eventPublisher;

    public ComplaintResponse createComplaint(CreateComplaintRequest request) {
        String ticketId = generateTicketId();
        int slaHours = SLA_HOURS.getOrDefault(request.getComplaintType(), 48);

        Complaint complaint = Complaint.builder()
                .ticketId(ticketId)
                .userId(request.getUserId())
                .accountId(request.getAccountId())
                .transactionId(request.getTransactionId())
                .productLine(request.getProductLine())
                .complaintType(request.getComplaintType())
                .description(request.getDescription())
                .status("ACCEPTED")
                .slaDeadline(LocalDateTime.now().plusHours(slaHours))
                .build();

        complaint = complaintRepository.save(complaint);
        log.info("Complaint created: ticketId={} type={} userId={}",
                ticketId, request.getComplaintType(), request.getUserId());

        eventPublisher.publish(ComplaintCreatedEvent.builder()
                .ticketId(ticketId)
                .userId(request.getUserId())
                .accountId(request.getAccountId())
                .transactionId(request.getTransactionId())
                .productLine(request.getProductLine())
                .complaintType(request.getComplaintType())
                .slaDeadlineHours(slaHours)
                .createdAt(complaint.getCreatedAt())
                .build());

        return ComplaintResponse.from(complaint);
    }

    @Transactional(readOnly = true)
    public ComplaintResponse getByTicketId(String ticketId, String requestingUserId) {
        Complaint complaint = complaintRepository.findByTicketId(ticketId)
                .orElseThrow(() -> new AppException("COMPLAINT_NOT_FOUND",
                        "Complaint " + ticketId + " not found"));

        if (!complaint.getUserId().equals(requestingUserId)) {
            throw new AppException("FORBIDDEN", "You are not authorised to view this complaint");
        }

        return ComplaintResponse.from(complaint);
    }

    @Transactional(readOnly = true)
    public List<ComplaintResponse> getByUserId(String userId) {
        return complaintRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(ComplaintResponse::from)
                .toList();
    }

    public ComplaintResponse updateStatus(String ticketId, UpdateStatusRequest request) {
        Complaint complaint = complaintRepository.findByTicketId(ticketId)
                .orElseThrow(() -> new AppException("COMPLAINT_NOT_FOUND",
                        "Complaint " + ticketId + " not found"));

        complaint.setStatus(request.getStatus());
        if (request.getOpsAnalystId() != null) {
            complaint.setOpsAnalystId(request.getOpsAnalystId());
        }
        if (request.getResolution() != null) {
            complaint.setResolution(request.getResolution());
        }
        if (request.getOutcome() != null) {
            complaint.setOutcome(request.getOutcome());
        }

        complaint = complaintRepository.save(complaint);
        log.info("Complaint {} status updated to {}", ticketId, request.getStatus());
        return ComplaintResponse.from(complaint);
    }

    private String generateTicketId() {
        String date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String suffix = UUID.randomUUID().toString().replace("-", "").substring(0, 6).toUpperCase();
        String candidate = "CMP-" + date + "-" + suffix;
        // Retry on the astronomically unlikely collision
        while (complaintRepository.existsByTicketId(candidate)) {
            suffix = UUID.randomUUID().toString().replace("-", "").substring(0, 6).toUpperCase();
            candidate = "CMP-" + date + "-" + suffix;
        }
        return candidate;
    }
}
