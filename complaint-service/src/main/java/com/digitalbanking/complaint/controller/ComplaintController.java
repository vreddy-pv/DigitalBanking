package com.digitalbanking.complaint.controller;

import com.digitalbanking.common.dto.ApiResponse;
import com.digitalbanking.complaint.dto.ComplaintResponse;
import com.digitalbanking.complaint.dto.CreateComplaintRequest;
import com.digitalbanking.complaint.dto.UpdateStatusRequest;
import com.digitalbanking.complaint.service.ComplaintService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/complaints")
@RequiredArgsConstructor
public class ComplaintController {

    private final ComplaintService complaintService;

    @PostMapping
    public ResponseEntity<ApiResponse<ComplaintResponse>> createComplaint(
            @Valid @RequestBody CreateComplaintRequest request) {
        ComplaintResponse response = complaintService.createComplaint(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.<ComplaintResponse>builder()
                        .success(true)
                        .code("COMPLAINT_CREATED")
                        .message("Complaint registered. Ticket ID: " + response.getTicketId())
                        .data(response)
                        .build());
    }

    @GetMapping("/{ticketId}")
    public ResponseEntity<ApiResponse<ComplaintResponse>> getComplaint(
            @PathVariable String ticketId,
            @RequestParam String userId) {
        ComplaintResponse response = complaintService.getByTicketId(ticketId, userId);
        return ResponseEntity.ok(ApiResponse.<ComplaintResponse>builder()
                .success(true)
                .code("COMPLAINT_RETRIEVED")
                .message("Complaint retrieved successfully")
                .data(response)
                .build());
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<ApiResponse<List<ComplaintResponse>>> getUserComplaints(
            @PathVariable String userId) {
        List<ComplaintResponse> complaints = complaintService.getByUserId(userId);
        return ResponseEntity.ok(ApiResponse.<List<ComplaintResponse>>builder()
                .success(true)
                .code("COMPLAINTS_RETRIEVED")
                .message("Complaints retrieved successfully")
                .data(complaints)
                .build());
    }

    @PutMapping("/{ticketId}/status")
    public ResponseEntity<ApiResponse<ComplaintResponse>> updateStatus(
            @PathVariable String ticketId,
            @Valid @RequestBody UpdateStatusRequest request) {
        ComplaintResponse response = complaintService.updateStatus(ticketId, request);
        return ResponseEntity.ok(ApiResponse.<ComplaintResponse>builder()
                .success(true)
                .code("COMPLAINT_STATUS_UPDATED")
                .message("Complaint status updated to " + response.getStatus())
                .data(response)
                .build());
    }

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        return ResponseEntity.ok(ApiResponse.<String>builder()
                .success(true)
                .code("SERVICE_HEALTHY")
                .message("Complaint Service is healthy")
                .data("UP")
                .build());
    }
}
