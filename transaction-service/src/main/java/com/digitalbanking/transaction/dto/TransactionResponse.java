package com.digitalbanking.transaction.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import com.fasterxml.jackson.annotation.JsonInclude;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TransactionResponse {

    private UUID id;

    private UUID fromAccountId;

    private UUID toAccountId;

    private String type;

    private BigDecimal amount;

    private String status;

    private String description;

    private String requestId;

    private LocalDateTime createdAt;

    private LocalDateTime completedAt;
}
