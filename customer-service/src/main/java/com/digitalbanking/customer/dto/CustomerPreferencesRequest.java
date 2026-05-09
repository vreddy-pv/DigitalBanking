package com.digitalbanking.customer.dto;

import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CustomerPreferencesRequest {

    private Boolean notificationEmail;

    private Boolean notificationSms;

    @Size(min = 2, max = 10, message = "Language code must be between 2 and 10 characters")
    private String language;
}
