package com.digitalbanking.complaint.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class CreateComplaintRequest {

    @NotBlank(message = "userId is required")
    private String userId;

    @NotBlank(message = "accountId is required")
    private String accountId;

    private String transactionId;

    @NotBlank(message = "productLine is required")
    @Pattern(regexp = "CASA|ML|USL", message = "productLine must be CASA, ML, or USL")
    private String productLine;

    @NotBlank(message = "complaintType is required")
    @Pattern(regexp = "UNAUTHORIZED|DISPUTE|FRAUD|ERROR",
             message = "complaintType must be UNAUTHORIZED, DISPUTE, FRAUD, or ERROR")
    private String complaintType;

    @NotBlank(message = "description is required")
    @Size(min = 10, max = 2000, message = "description must be between 10 and 2000 characters")
    private String description;
}
