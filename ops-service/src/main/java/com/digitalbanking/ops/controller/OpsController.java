package com.digitalbanking.ops.controller;

import com.digitalbanking.common.dto.ApiResponse;
import com.digitalbanking.ops.dto.*;
import com.digitalbanking.ops.service.OpsCaseService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/ops")
@RequiredArgsConstructor
public class OpsController {

    private final OpsCaseService opsCaseService;

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        return ResponseEntity.ok(ApiResponse.<String>builder()
                .success(true)
                .code("SERVICE_HEALTHY")
                .message("Ops Service is healthy")
                .data("UP")
                .build());
    }

    @GetMapping("/stats")
    public ResponseEntity<ApiResponse<OpsStatsResponse>> getStats() {
        OpsStatsResponse stats = opsCaseService.getStats();
        return ResponseEntity.ok(ApiResponse.<OpsStatsResponse>builder()
                .success(true)
                .code("STATS_RETRIEVED")
                .message("Operations statistics retrieved")
                .data(stats)
                .build());
    }

    @GetMapping("/cases")
    public ResponseEntity<ApiResponse<List<CaseResponse>>> listCases(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String assignedTo) {
        List<CaseResponse> cases = opsCaseService.listCases(status, assignedTo);
        return ResponseEntity.ok(ApiResponse.<List<CaseResponse>>builder()
                .success(true)
                .code("CASES_RETRIEVED")
                .message("Cases retrieved: " + cases.size())
                .data(cases)
                .build());
    }

    @GetMapping("/cases/{ticketId}")
    public ResponseEntity<ApiResponse<CaseResponse>> getCase(@PathVariable String ticketId) {
        CaseResponse response = opsCaseService.getCase(ticketId);
        return ResponseEntity.ok(ApiResponse.<CaseResponse>builder()
                .success(true)
                .code("CASE_RETRIEVED")
                .message("Case retrieved: " + ticketId)
                .data(response)
                .build());
    }

    @PutMapping("/cases/{ticketId}/assign")
    public ResponseEntity<ApiResponse<CaseResponse>> assignCase(
            @PathVariable String ticketId,
            @Valid @RequestBody AssignCaseRequest request) {
        CaseResponse response = opsCaseService.assignCase(ticketId, request);
        return ResponseEntity.ok(ApiResponse.<CaseResponse>builder()
                .success(true)
                .code("CASE_ASSIGNED")
                .message("Case " + ticketId + " assigned to " + request.getAnalystId())
                .data(response)
                .build());
    }

    @PutMapping("/cases/{ticketId}/resolve")
    public ResponseEntity<ApiResponse<CaseResponse>> resolveCase(
            @PathVariable String ticketId,
            @Valid @RequestBody ResolveCaseRequest request) {
        CaseResponse response = opsCaseService.resolveCase(ticketId, request);
        return ResponseEntity.ok(ApiResponse.<CaseResponse>builder()
                .success(true)
                .code("CASE_RESOLVED")
                .message("Case " + ticketId + " " + request.getOutcome().toLowerCase())
                .data(response)
                .build());
    }
}
