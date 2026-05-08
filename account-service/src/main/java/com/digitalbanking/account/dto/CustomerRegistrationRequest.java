package com.digitalbanking.account.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import jakarta.validation.constraints.*;
import java.time.LocalDate;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CustomerRegistrationRequest {

    @NotBlank(message = "User ID is required")
    private String userId;

    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 255, message = "Name must be between 2 and 255 characters")
    private String name;

    @NotNull(message = "Date of birth is required")
    @PastOrPresent(message = "Date of birth must be in the past")
    private LocalDate dob;

    @NotBlank(message = "Email is required")
    @Email(message = "Email should be valid")
    private String email;

    private String phone;

    private String addressLine1;

    private String addressLine2;

    private String city;

    private String state;

    private String zipCode;

    private String country;

    @Pattern(regexp = "^[A-Z]{5}[0-9]{4}[A-Z]{1}$", message = "Invalid PAN format")
    private String pan;

    @Pattern(regexp = "^[0-9]{12}$", message = "Aadhar must be 12 digits")
    private String aadhar;

    @NotNull(message = "Account type is required")
    private String accountType;
}
