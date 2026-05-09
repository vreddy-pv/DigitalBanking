package com.digitalbanking.customer.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KycStatusUpdateRequest {

    @NotBlank(message = "Status is required")
    @Pattern(
        regexp = "VERIFIED|REJECTED",
        message = "Status must be VERIFIED or REJECTED"
    )
    private String status;

    private String rejectionReason;
}
