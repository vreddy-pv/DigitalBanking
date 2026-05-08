package com.digitalbanking.account.service;

import com.digitalbanking.account.dto.AccountResponse;
import com.digitalbanking.account.dto.CustomerRegistrationRequest;
import com.digitalbanking.account.dto.CustomerResponse;
import com.digitalbanking.account.entity.Account;
import com.digitalbanking.account.entity.Customer;
import com.digitalbanking.account.repository.AccountRepository;
import com.digitalbanking.account.repository.CustomerRepository;
import com.digitalbanking.common.exception.AppException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.time.LocalDate;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

public class AccountServiceTest {

    private AccountService accountService;

    @Mock
    private CustomerRepository customerRepository;

    @Mock
    private AccountRepository accountRepository;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        accountService = new AccountService(customerRepository, accountRepository);
    }

    @Test
    void testRegisterCustomer_Success() {
        UUID userId = UUID.randomUUID();
        UUID customerId = UUID.randomUUID();
        CustomerRegistrationRequest request = CustomerRegistrationRequest.builder()
                .userId(userId.toString())
                .name("John Doe")
                .dob(LocalDate.of(1990, 1, 1))
                .email("john@example.com")
                .phone("1234567890")
                .addressLine1("123 Main St")
                .city("New York")
                .state("NY")
                .zipCode("10001")
                .country("USA")
                .pan("ABCDE1234F")
                .aadhar("123456789012")
                .accountType("SAVINGS")
                .build();

        Customer customer = Customer.builder()
                .id(customerId)
                .userId(userId)
                .name(request.getName())
                .dob(request.getDob())
                .email(request.getEmail())
                .phone(request.getPhone())
                .addressLine1(request.getAddressLine1())
                .city(request.getCity())
                .state(request.getState())
                .zipCode(request.getZipCode())
                .country(request.getCountry())
                .pan(request.getPan())
                .aadhar(request.getAadhar())
                .kycStatus("PENDING")
                .build();

        Account account = Account.builder()
                .id(UUID.randomUUID())
                .customerId(customerId)
                .accountNumber("ACC1234567890123")
                .accountType(request.getAccountType())
                .status("ACTIVE")
                .build();

        when(customerRepository.existsByUserId(userId)).thenReturn(false);
        when(customerRepository.existsByEmail(request.getEmail())).thenReturn(false);
        when(customerRepository.save(any(Customer.class))).thenReturn(customer);
        when(customerRepository.findById(customerId)).thenReturn(java.util.Optional.of(customer));
        when(accountRepository.existsByAccountNumber(any(String.class))).thenReturn(false);
        when(accountRepository.save(any(Account.class))).thenReturn(account);

        CustomerResponse response = accountService.registerCustomer(request);

        assertNotNull(response);
        assertEquals(customerId, response.getId());
        assertEquals(userId, response.getUserId());
        assertEquals(request.getName(), response.getName());

        verify(customerRepository).save(any(Customer.class));
        verify(accountRepository).save(any(Account.class));
    }

    @Test
    void testRegisterCustomer_CustomerAlreadyExists() {
        UUID userId = UUID.randomUUID();
        CustomerRegistrationRequest request = CustomerRegistrationRequest.builder()
                .userId(userId.toString())
                .name("John Doe")
                .dob(LocalDate.of(1990, 1, 1))
                .email("john@example.com")
                .accountType("SAVINGS")
                .build();

        when(customerRepository.existsByUserId(userId)).thenReturn(true);

        assertThrows(AppException.class, () -> accountService.registerCustomer(request));
    }

    @Test
    void testRegisterCustomer_EmailAlreadyExists() {
        UUID userId = UUID.randomUUID();
        CustomerRegistrationRequest request = CustomerRegistrationRequest.builder()
                .userId(userId.toString())
                .name("John Doe")
                .dob(LocalDate.of(1990, 1, 1))
                .email("john@example.com")
                .accountType("SAVINGS")
                .build();

        when(customerRepository.existsByUserId(userId)).thenReturn(false);
        when(customerRepository.existsByEmail(request.getEmail())).thenReturn(true);

        assertThrows(AppException.class, () -> accountService.registerCustomer(request));
    }

    @Test
    void testGetCustomerById_Success() {
        UUID customerId = UUID.randomUUID();
        Customer customer = Customer.builder()
                .id(customerId)
                .userId(UUID.randomUUID())
                .name("John Doe")
                .dob(LocalDate.of(1990, 1, 1))
                .email("john@example.com")
                .kycStatus("PENDING")
                .build();

        when(customerRepository.findById(customerId)).thenReturn(Optional.of(customer));

        CustomerResponse response = accountService.getCustomerById(customerId);

        assertNotNull(response);
        assertEquals(customerId, response.getId());
        assertEquals("John Doe", response.getName());
    }

    @Test
    void testGetCustomerById_NotFound() {
        UUID customerId = UUID.randomUUID();

        when(customerRepository.findById(customerId)).thenReturn(Optional.empty());

        assertThrows(AppException.class, () -> accountService.getCustomerById(customerId));
    }

    @Test
    void testGetAccountById_Success() {
        UUID accountId = UUID.randomUUID();
        Account account = Account.builder()
                .id(accountId)
                .customerId(UUID.randomUUID())
                .accountNumber("ACC1234567890123")
                .accountType("SAVINGS")
                .status("ACTIVE")
                .build();

        when(accountRepository.findById(accountId)).thenReturn(Optional.of(account));

        AccountResponse response = accountService.getAccountById(accountId);

        assertNotNull(response);
        assertEquals(accountId, response.getId());
        assertEquals("ACTIVE", response.getStatus());
    }

    @Test
    void testUpdateAccountStatus_Success() {
        UUID accountId = UUID.randomUUID();
        Account account = Account.builder()
                .id(accountId)
                .customerId(UUID.randomUUID())
                .accountNumber("ACC1234567890123")
                .accountType("SAVINGS")
                .status("ACTIVE")
                .build();

        when(accountRepository.findById(accountId)).thenReturn(Optional.of(account));
        when(accountRepository.save(any(Account.class))).thenReturn(account);

        assertDoesNotThrow(() -> accountService.updateAccountStatus(accountId, "FROZEN"));

        verify(accountRepository).save(any(Account.class));
    }
}
