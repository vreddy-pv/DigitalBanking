package com.digitalbanking.account.service;

import com.digitalbanking.account.dto.AccountResponse;
import com.digitalbanking.account.dto.CustomerRegistrationRequest;
import com.digitalbanking.account.dto.CustomerResponse;
import com.digitalbanking.account.entity.Account;
import com.digitalbanking.account.entity.Customer;
import com.digitalbanking.account.repository.AccountRepository;
import com.digitalbanking.account.repository.CustomerRepository;
import com.digitalbanking.common.exception.AppException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class AccountService {

    private final CustomerRepository customerRepository;
    private final AccountRepository accountRepository;

    public CustomerResponse registerCustomer(CustomerRegistrationRequest request) {
        UUID userId = UUID.fromString(request.getUserId());

        if (customerRepository.existsByUserId(userId)) {
            throw new AppException("CUSTOMER_ALREADY_EXISTS", "Customer with this user ID already exists", userId.toString());
        }

        if (customerRepository.existsByEmail(request.getEmail())) {
            throw new AppException("EMAIL_ALREADY_EXISTS", "Email is already registered", userId.toString());
        }

        Customer customer = Customer.builder()
                .userId(userId)
                .name(request.getName())
                .dob(request.getDob())
                .email(request.getEmail())
                .phone(request.getPhone())
                .addressLine1(request.getAddressLine1())
                .addressLine2(request.getAddressLine2())
                .city(request.getCity())
                .state(request.getState())
                .zipCode(request.getZipCode())
                .country(request.getCountry())
                .pan(request.getPan())
                .aadhar(request.getAadhar())
                .kycStatus("PENDING")
                .build();

        customer = customerRepository.save(customer);

        createAccount(customer.getId(), request.getAccountType());

        log.info("Customer registered successfully with ID: {}", customer.getId());

        return mapToCustomerResponse(customer);
    }

    public AccountResponse createAccount(UUID customerId, String accountType) {
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new AppException("CUSTOMER_NOT_FOUND", "Customer not found", customerId.toString()));

        String accountNumber = generateAccountNumber();

        if (accountRepository.existsByAccountNumber(accountNumber)) {
            throw new AppException("ACCOUNT_NUMBER_EXISTS", "Account number already exists", customerId.toString());
        }

        Account account = Account.builder()
                .customerId(customerId)
                .accountNumber(accountNumber)
                .accountType(accountType)
                .status("ACTIVE")
                .build();

        account = accountRepository.save(account);

        log.info("Account created with number: {} for customer: {}", accountNumber, customerId);

        return mapToAccountResponse(account);
    }

    public CustomerResponse getCustomerById(UUID customerId) {
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new AppException("CUSTOMER_NOT_FOUND", "Customer not found", customerId.toString()));

        return mapToCustomerResponse(customer);
    }

    public CustomerResponse getCustomerByUserId(UUID userId) {
        Customer customer = customerRepository.findByUserId(userId)
                .orElseThrow(() -> new AppException("CUSTOMER_NOT_FOUND", "Customer not found", userId.toString()));

        return mapToCustomerResponse(customer);
    }

    public AccountResponse getAccountById(UUID accountId) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new AppException("ACCOUNT_NOT_FOUND", "Account not found", accountId.toString()));

        return mapToAccountResponse(account);
    }

    public AccountResponse getAccountByNumber(String accountNumber) {
        Account account = accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow(() -> new AppException("ACCOUNT_NOT_FOUND", "Account not found", accountNumber));

        return mapToAccountResponse(account);
    }

    public List<AccountResponse> getAccountsByCustomerId(UUID customerId) {
        List<Account> accounts = accountRepository.findByCustomerId(customerId);
        return accounts.stream()
                .map(this::mapToAccountResponse)
                .collect(Collectors.toList());
    }

    public CustomerResponse updateCustomerProfile(UUID customerId, CustomerRegistrationRequest request) {
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new AppException("CUSTOMER_NOT_FOUND", "Customer not found", customerId.toString()));

        if (!customer.getEmail().equals(request.getEmail()) && customerRepository.existsByEmail(request.getEmail())) {
            throw new AppException("EMAIL_ALREADY_EXISTS", "Email is already registered", customerId.toString());
        }

        customer.setName(request.getName());
        customer.setDob(request.getDob());
        customer.setEmail(request.getEmail());
        customer.setPhone(request.getPhone());
        customer.setAddressLine1(request.getAddressLine1());
        customer.setAddressLine2(request.getAddressLine2());
        customer.setCity(request.getCity());
        customer.setState(request.getState());
        customer.setZipCode(request.getZipCode());
        customer.setCountry(request.getCountry());
        customer.setPan(request.getPan());
        customer.setAadhar(request.getAadhar());

        customer = customerRepository.save(customer);

        log.info("Customer profile updated for ID: {}", customerId);

        return mapToCustomerResponse(customer);
    }

    public void updateAccountStatus(UUID accountId, String newStatus) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new AppException("ACCOUNT_NOT_FOUND", "Account not found", accountId.toString()));

        account.setStatus(newStatus);
        if ("CLOSED".equals(newStatus)) {
            account.setClosedAt(LocalDateTime.now());
        }

        accountRepository.save(account);

        log.info("Account status updated to: {} for account ID: {}", newStatus, accountId);
    }

    private String generateAccountNumber() {
        return "ACC" + UUID.randomUUID().toString().substring(0, 17).toUpperCase();
    }

    private CustomerResponse mapToCustomerResponse(Customer customer) {
        return CustomerResponse.builder()
                .id(customer.getId())
                .userId(customer.getUserId())
                .name(customer.getName())
                .dob(customer.getDob())
                .email(customer.getEmail())
                .phone(customer.getPhone())
                .addressLine1(customer.getAddressLine1())
                .addressLine2(customer.getAddressLine2())
                .city(customer.getCity())
                .state(customer.getState())
                .zipCode(customer.getZipCode())
                .country(customer.getCountry())
                .pan(customer.getPan())
                .aadhar(customer.getAadhar())
                .kycStatus(customer.getKycStatus())
                .kycVerifiedAt(customer.getKycVerifiedAt())
                .createdAt(customer.getCreatedAt())
                .updatedAt(customer.getUpdatedAt())
                .build();
    }

    private AccountResponse mapToAccountResponse(Account account) {
        return AccountResponse.builder()
                .id(account.getId())
                .customerId(account.getCustomerId())
                .accountNumber(account.getAccountNumber())
                .accountType(account.getAccountType())
                .status(account.getStatus())
                .createdAt(account.getCreatedAt())
                .closedAt(account.getClosedAt())
                .build();
    }
}
