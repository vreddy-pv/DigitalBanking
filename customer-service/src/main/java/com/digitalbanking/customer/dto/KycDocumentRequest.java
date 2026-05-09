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
public class KycDocumentRequest {

    @NotBlank(message = "Document type is required")
    @Pattern(
        regexp = "PASSPORT|NATIONAL_ID|DRIVING_LICENSE|PAN_CARD|UTILITY_BILL",
        message = "Document type must be one of: PASSPORT, NATIONAL_ID, DRIVING_LICENSE, PAN_CARD, UTILITY_BILL"
    )
    private String documentType;

    @NotBlank(message = "Document reference is required")
    private String documentReference;
}
