package com.digitalbanking.ops.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

@Data
public class ResolveCaseRequest {

    @NotBlank(message = "outcome is required")
    @Pattern(regexp = "RESOLVED|ESCALATED|REJECTED",
             message = "outcome must be RESOLVED, ESCALATED, or REJECTED")
    private String outcome;

    private String opsNotes;
}
