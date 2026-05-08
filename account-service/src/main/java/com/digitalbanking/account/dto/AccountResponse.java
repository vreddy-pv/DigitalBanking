package com.digitalbanking.account.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import com.fasterxml.jackson.annotation.JsonInclude;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class AccountResponse {

    private UUID id;

    private UUID customerId;

    private String accountNumber;

    private String accountType;

    private String status;

    private LocalDateTime createdAt;

    private LocalDateTime closedAt;
}
