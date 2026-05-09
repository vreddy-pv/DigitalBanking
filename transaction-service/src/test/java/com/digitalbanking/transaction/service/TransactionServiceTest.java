package com.digitalbanking.transaction.service;

import com.digitalbanking.common.event.TransactionCreatedEvent;
import com.digitalbanking.transaction.client.AccountServiceClient;
import com.digitalbanking.transaction.client.AccountServiceClient.AccountData;
import com.digitalbanking.transaction.client.AccountServiceClient.CustomerData;
import com.digitalbanking.transaction.dto.DepositRequest;
import com.digitalbanking.transaction.dto.TransactionResponse;
import com.digitalbanking.transaction.dto.TransferRequest;
import com.digitalbanking.transaction.dto.WithdrawalRequest;
import com.digitalbanking.transaction.entity.Transaction;
import com.digitalbanking.transaction.repository.TransactionAuditRepository;
import com.digitalbanking.transaction.repository.TransactionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.context.ApplicationEventPublisher;

import java.math.BigDecimal;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TransactionServiceTest {

    @Mock
    private TransactionRepository transactionRepository;

    @Mock
    private TransactionAuditRepository transactionAuditRepository;

    @Mock
    private ApplicationEventPublisher eventPublisher;

    @Mock
    private RabbitTemplate rabbitTemplate;

    @Mock
    private AccountServiceClient accountServiceClient;

    private TransactionService transactionService;

    @BeforeEach
    void setUp() {
        transactionService = new TransactionService(
                transactionRepository,
                transactionAuditRepository,
                eventPublisher,
                rabbitTemplate,
                accountServiceClient
        );
    }

    // -----------------------------------------------------------------------
    // Deposit — AccountServiceClient resolves real customer data
    // -----------------------------------------------------------------------

    @Test
    void deposit_publishesEvent_withEnrichedCustomerData_whenAccountServiceSucceeds() {
        UUID toAccountId = UUID.randomUUID();
        UUID customerId = UUID.randomUUID();
        String requestId = UUID.randomUUID().toString();

        AccountData accountData = new AccountData(toAccountId, customerId, "ACC6D6F95B8-3F14-4FA");
        CustomerData customerData = new CustomerData(customerId, "Jane Doe", "jane@example.com");

        when(transactionRepository.findByRequestId(requestId)).thenReturn(Optional.empty());
        when(transactionRepository.save(any(Transaction.class))).thenAnswer(inv -> {
            Transaction t = inv.getArgument(0);
            t.setId(UUID.randomUUID());
            return t;
        });
        when(accountServiceClient.getAccountById(toAccountId)).thenReturn(Optional.of(accountData));
        when(accountServiceClient.getCustomerById(customerId)).thenReturn(Optional.of(customerData));

        DepositRequest request = new DepositRequest();
        request.setToAccountId(toAccountId.toString());
        request.setAmount(BigDecimal.valueOf(500));
        request.setRequestId(requestId);
        request.setDescription("Test deposit");

        transactionService.deposit(request);

        // Capture the event sent to RabbitMQ
        ArgumentCaptor<TransactionCreatedEvent> eventCaptor =
                ArgumentCaptor.forClass(TransactionCreatedEvent.class);
        verify(rabbitTemplate).convertAndSend(anyString(), anyString(), eventCaptor.capture());

        TransactionCreatedEvent published = eventCaptor.getValue();
        assertThat(published.getRecipientEmail()).isEqualTo("jane@example.com");
        assertThat(published.getCustomerName()).isEqualTo("Jane Doe");
        assertThat(published.getAccountNumber()).isEqualTo("ACC6D6F95B8-3F14-4FA");
    }

    // -----------------------------------------------------------------------
    // Deposit — AccountServiceClient fails gracefully (empty Optional)
    // -----------------------------------------------------------------------

    @Test
    void deposit_publishesEvent_withEmptyFields_whenAccountServiceFails() {
        UUID toAccountId = UUID.randomUUID();
        String requestId = UUID.randomUUID().toString();

        when(transactionRepository.findByRequestId(requestId)).thenReturn(Optional.empty());
        when(transactionRepository.save(any(Transaction.class))).thenAnswer(inv -> {
            Transaction t = inv.getArgument(0);
            t.setId(UUID.randomUUID());
            return t;
        });
        when(accountServiceClient.getAccountById(toAccountId)).thenReturn(Optional.empty());

        DepositRequest request = new DepositRequest();
        request.setToAccountId(toAccountId.toString());
        request.setAmount(BigDecimal.valueOf(200));
        request.setRequestId(requestId);
        request.setDescription("Test deposit - degraded");

        // Should not throw
        transactionService.deposit(request);

        ArgumentCaptor<TransactionCreatedEvent> eventCaptor =
                ArgumentCaptor.forClass(TransactionCreatedEvent.class);
        verify(rabbitTemplate).convertAndSend(anyString(), anyString(), eventCaptor.capture());

        TransactionCreatedEvent published = eventCaptor.getValue();
        assertThat(published.getRecipientEmail()).isEqualTo("");
        assertThat(published.getCustomerName()).isEqualTo("");
        // Falls back to the UUID string
        assertThat(published.getAccountNumber()).isEqualTo(toAccountId.toString());
    }

    // -----------------------------------------------------------------------
    // Withdrawal — fromAccountId is used for lookup when toAccountId is null
    // -----------------------------------------------------------------------

    @Test
    void withdrawal_publishesEvent_withEnrichedData_usingFromAccountId() {
        UUID fromAccountId = UUID.randomUUID();
        UUID customerId = UUID.randomUUID();
        String requestId = UUID.randomUUID().toString();

        AccountData accountData = new AccountData(fromAccountId, customerId, "ACCABC123");
        CustomerData customerData = new CustomerData(customerId, "John Smith", "john@example.com");

        when(transactionRepository.findByRequestId(requestId)).thenReturn(Optional.empty());
        when(transactionRepository.save(any(Transaction.class))).thenAnswer(inv -> {
            Transaction t = inv.getArgument(0);
            t.setId(UUID.randomUUID());
            return t;
        });
        // For WITHDRAWAL toAccountId is null, so lookupAccountId = fromAccountId
        when(accountServiceClient.getAccountById(fromAccountId)).thenReturn(Optional.of(accountData));
        when(accountServiceClient.getCustomerById(customerId)).thenReturn(Optional.of(customerData));

        WithdrawalRequest request = new WithdrawalRequest();
        request.setFromAccountId(fromAccountId.toString());
        request.setAmount(BigDecimal.valueOf(100));
        request.setRequestId(requestId);
        request.setDescription("Test withdrawal");

        transactionService.withdraw(request);

        ArgumentCaptor<TransactionCreatedEvent> eventCaptor =
                ArgumentCaptor.forClass(TransactionCreatedEvent.class);
        verify(rabbitTemplate).convertAndSend(anyString(), anyString(), eventCaptor.capture());

        TransactionCreatedEvent published = eventCaptor.getValue();
        assertThat(published.getRecipientEmail()).isEqualTo("john@example.com");
        assertThat(published.getCustomerName()).isEqualTo("John Smith");
        assertThat(published.getAccountNumber()).isEqualTo("ACCABC123");
    }

    // -----------------------------------------------------------------------
    // Transfer — toAccountId takes priority for notification
    // -----------------------------------------------------------------------

    @Test
    void transfer_publishesEvent_usingToAccountId_forNotification() {
        UUID fromAccountId = UUID.randomUUID();
        UUID toAccountId = UUID.randomUUID();
        UUID customerId = UUID.randomUUID();
        String requestId = UUID.randomUUID().toString();

        AccountData toAccountData = new AccountData(toAccountId, customerId, "ACCTRANSFER99");
        CustomerData customerData = new CustomerData(customerId, "Alice", "alice@example.com");

        when(transactionRepository.findByRequestId(requestId)).thenReturn(Optional.empty());
        when(transactionRepository.save(any(Transaction.class))).thenAnswer(inv -> {
            Transaction t = inv.getArgument(0);
            t.setId(UUID.randomUUID());
            return t;
        });
        // toAccountId takes priority
        when(accountServiceClient.getAccountById(toAccountId)).thenReturn(Optional.of(toAccountData));
        when(accountServiceClient.getCustomerById(customerId)).thenReturn(Optional.of(customerData));

        TransferRequest request = new TransferRequest();
        request.setFromAccountId(fromAccountId.toString());
        request.setToAccountId(toAccountId.toString());
        request.setAmount(BigDecimal.valueOf(750));
        request.setRequestId(requestId);
        request.setDescription("Test transfer");

        transactionService.transfer(request);

        ArgumentCaptor<TransactionCreatedEvent> eventCaptor =
                ArgumentCaptor.forClass(TransactionCreatedEvent.class);
        verify(rabbitTemplate).convertAndSend(anyString(), anyString(), eventCaptor.capture());

        TransactionCreatedEvent published = eventCaptor.getValue();
        assertThat(published.getRecipientEmail()).isEqualTo("alice@example.com");
        assertThat(published.getCustomerName()).isEqualTo("Alice");
        assertThat(published.getAccountNumber()).isEqualTo("ACCTRANSFER99");
    }

    // -----------------------------------------------------------------------
    // Dual publish: both RabbitMQ and ApplicationEventPublisher receive the event
    // -----------------------------------------------------------------------

    @Test
    void deposit_dualPublishes_toRabbitMQ_and_eventPublisher() {
        UUID toAccountId = UUID.randomUUID();
        String requestId = UUID.randomUUID().toString();

        when(transactionRepository.findByRequestId(requestId)).thenReturn(Optional.empty());
        when(transactionRepository.save(any(Transaction.class))).thenAnswer(inv -> {
            Transaction t = inv.getArgument(0);
            t.setId(UUID.randomUUID());
            return t;
        });
        when(accountServiceClient.getAccountById(any())).thenReturn(Optional.empty());

        DepositRequest request = new DepositRequest();
        request.setToAccountId(toAccountId.toString());
        request.setAmount(BigDecimal.valueOf(100));
        request.setRequestId(requestId);

        transactionService.deposit(request);

        verify(rabbitTemplate, times(1)).convertAndSend(anyString(), anyString(), any(TransactionCreatedEvent.class));
        verify(eventPublisher, times(1)).publishEvent(any(TransactionCreatedEvent.class));
    }
}
