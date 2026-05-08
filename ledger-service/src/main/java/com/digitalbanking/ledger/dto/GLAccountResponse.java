package com.digitalbanking.ledger.dto;

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
public class GLAccountResponse {

    private UUID id;

    private String code;

    private String name;

    private String type;

    private BigDecimal balance;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
