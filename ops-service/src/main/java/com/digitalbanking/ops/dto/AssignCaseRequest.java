package com.digitalbanking.ops.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class AssignCaseRequest {

    @NotBlank(message = "analystId is required")
    private String analystId;
}
