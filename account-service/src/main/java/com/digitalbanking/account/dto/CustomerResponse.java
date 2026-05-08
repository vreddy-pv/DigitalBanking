package com.digitalbanking.account.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import com.fasterxml.jackson.annotation.JsonInclude;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class CustomerResponse {

    private UUID id;

    private UUID userId;

    private String name;

    private LocalDate dob;

    private String email;

    private String phone;

    private String addressLine1;

    private String addressLine2;

    private String city;

    private String state;

    private String zipCode;

    private String country;

    private String pan;

    private String aadhar;

    private String kycStatus;

    private LocalDateTime kycVerifiedAt;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
