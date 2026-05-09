package com.digitalbanking.customer.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class BeneficiaryResponse {

    private UUID id;
    private UUID ownerAccountId;
    private UUID beneficiaryAccountId;
    private String nickname;
    private Boolean active;
    private LocalDateTime createdAt;
}
