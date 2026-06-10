package com.digitalbanking.complaint.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

@Data
public class UpdateStatusRequest {

    @NotBlank(message = "status is required")
    @Pattern(regexp = "UNDER_INVESTIGATION|RESOLVED|ESCALATED|REJECTED",
             message = "status must be UNDER_INVESTIGATION, RESOLVED, ESCALATED, or REJECTED")
    private String status;

    private String opsAnalystId;
    private String resolution;

    @Pattern(regexp = "RESOLVED|ESCALATED|REJECTED",
             message = "outcome must be RESOLVED, ESCALATED, or REJECTED")
    private String outcome;
}
