package com.digitalbanking.transaction.service;

import com.digitalbanking.transaction.client.AccountServiceClient;
import com.digitalbanking.transaction.client.AccountServiceClient.AccountData;
import com.digitalbanking.transaction.client.AccountServiceClient.CustomerData;
import com.digitalbanking.transaction.dto.DepositRequest;
import com.digitalbanking.transaction.dto.TransactionResponse;
import com.digitalbanking.transaction.dto.TransferRequest;
import com.digitalbanking.transaction.dto.WithdrawalRequest;
import com.digitalbanking.transaction.entity.Transaction;
import com.digitalbanking.transaction.entity.TransactionAudit;
import com.digitalbanking.transaction.repository.TransactionAuditRepository;
import com.digitalbanking.transaction.repository.TransactionRepository;
import com.digitalbanking.common.exception.AppException;
import com.digitalbanking.common.event.TransactionCreatedEvent;
import com.digitalbanking.transaction.config.RabbitMQConfig;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class TransactionService {

    private final TransactionRepository transactionRepository;
    private final TransactionAuditRepository transactionAuditRepository;
    private final ApplicationEventPublisher eventPublisher;
    private final RabbitTemplate rabbitTemplate;
    private final AccountServiceClient accountServiceClient;

    public TransactionResponse deposit(DepositRequest request) {
        UUID toAccountId = UUID.fromString(request.getToAccountId());

        Optional<Transaction> existing = transactionRepository.findByRequestId(request.getRequestId());
        if (existing.isPresent()) {
            log.info("Idempotent deposit - returning existing transaction: {}", existing.get().getId());
            return mapToResponse(existing.get());
        }

        Transaction transaction = Transaction.builder()
                .toAccountId(toAccountId)
                .type("DEPOSIT")
                .amount(request.getAmount())
                .status("PENDING")
                .description(request.getDescription())
                .requestId(request.getRequestId())
                .build();

        transaction = transactionRepository.save(transaction);

        publishTransactionCreatedEvent(transaction);

        log.info("Deposit transaction created: {} for account: {}", transaction.getId(), toAccountId);

        return mapToResponse(transaction);
    }

    public TransactionResponse withdraw(WithdrawalRequest request) {
        UUID fromAccountId = UUID.fromString(request.getFromAccountId());

        Optional<Transaction> existing = transactionRepository.findByRequestId(request.getRequestId());
        if (existing.isPresent()) {
            log.info("Idempotent withdrawal - returning existing transaction: {}", existing.get().getId());
            return mapToResponse(existing.get());
        }

        Transaction transaction = Transaction.builder()
                .fromAccountId(fromAccountId)
                .type("WITHDRAWAL")
                .amount(request.getAmount())
                .status("PENDING")
                .description(request.getDescription())
                .requestId(request.getRequestId())
                .build();

        transaction = transactionRepository.save(transaction);

        publishTransactionCreatedEvent(transaction);

        log.info("Withdrawal transaction created: {} for account: {}", transaction.getId(), fromAccountId);

        return mapToResponse(transaction);
    }

    public TransactionResponse transfer(TransferRequest request) {
        UUID fromAccountId = UUID.fromString(request.getFromAccountId());
        UUID toAccountId = UUID.fromString(request.getToAccountId());

        if (fromAccountId.equals(toAccountId)) {
            throw new AppException("INVALID_TRANSFER", "Cannot transfer to the same account", request.getRequestId());
        }

        Optional<Transaction> existing = transactionRepository.findByRequestId(request.getRequestId());
        if (existing.isPresent()) {
            log.info("Idempotent transfer - returning existing transaction: {}", existing.get().getId());
            return mapToResponse(existing.get());
        }

        Transaction transaction = Transaction.builder()
                .fromAccountId(fromAccountId)
                .toAccountId(toAccountId)
                .type("TRANSFER")
                .amount(request.getAmount())
                .status("PENDING")
                .description(request.getDescription())
                .requestId(request.getRequestId())
                .build();

        transaction = transactionRepository.save(transaction);

        publishTransactionCreatedEvent(transaction);

        log.info("Transfer transaction created: {} from {} to {}", transaction.getId(), fromAccountId, toAccountId);

        return mapToResponse(transaction);
    }

    public TransactionResponse getTransactionById(UUID transactionId) {
        Transaction transaction = transactionRepository.findById(transactionId)
                .orElseThrow(() -> new AppException("TRANSACTION_NOT_FOUND", "Transaction not found", transactionId.toString()));

        return mapToResponse(transaction);
    }

    public List<TransactionResponse> getTransactionsByAccountId(UUID accountId) {
        List<Transaction> transactions = transactionRepository
                .findByFromAccountIdOrToAccountIdOrderByCreatedAtDesc(accountId, accountId);

        return transactions.stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    public void completeTransaction(UUID transactionId) {
        Transaction transaction = transactionRepository.findById(transactionId)
                .orElseThrow(() -> new AppException("TRANSACTION_NOT_FOUND", "Transaction not found", transactionId.toString()));

        String statusBefore = transaction.getStatus();
        transaction.setStatus("COMPLETED");
        transaction.setCompletedAt(LocalDateTime.now());
        transactionRepository.save(transaction);

        createAuditEntry(transactionId, statusBefore, "COMPLETED", "Ledger processed successfully");

        log.info("Transaction completed: {}", transactionId);
    }

    public void failTransaction(UUID transactionId, String reason) {
        Transaction transaction = transactionRepository.findById(transactionId)
                .orElseThrow(() -> new AppException("TRANSACTION_NOT_FOUND", "Transaction not found", transactionId.toString()));

        String statusBefore = transaction.getStatus();
        transaction.setStatus("FAILED");
        transaction.setCompletedAt(LocalDateTime.now());
        transactionRepository.save(transaction);

        createAuditEntry(transactionId, statusBefore, "FAILED", reason);

        log.warn("Transaction failed: {} - {}", transactionId, reason);
    }

    private void publishTransactionCreatedEvent(Transaction transaction) {
        // Determine which account to look up for notification
        UUID lookupAccountId = transaction.getToAccountId() != null
                ? transaction.getToAccountId()
                : transaction.getFromAccountId();

        // Fetch enrichment data — graceful degradation on failure
        String recipientEmail = "";
        String customerName = "";
        String accountNumber = lookupAccountId != null ? lookupAccountId.toString() : "";

        if (lookupAccountId != null) {
            Optional<AccountData> accountOpt = accountServiceClient.getAccountById(lookupAccountId);
            if (accountOpt.isPresent()) {
                accountNumber = accountOpt.get().accountNumber();
                Optional<CustomerData> customerOpt = accountServiceClient.getCustomerById(accountOpt.get().customerId());
                if (customerOpt.isPresent()) {
                    recipientEmail = customerOpt.get().email() != null ? customerOpt.get().email() : "";
                    customerName = customerOpt.get().name() != null ? customerOpt.get().name() : "";
                }
            }
        }

        TransactionCreatedEvent event = TransactionCreatedEvent.builder()
                .transactionId(transaction.getId())
                .fromAccountId(transaction.getFromAccountId())
                .toAccountId(transaction.getToAccountId())
                .type(transaction.getType())
                .amount(transaction.getAmount())
                .description(transaction.getDescription())
                .timestamp(System.currentTimeMillis())
                .recipientEmail(recipientEmail)
                .customerName(customerName)
                .accountNumber(accountNumber)
                .build();

        // Publish to RabbitMQ so the Notification Service (Python/FastAPI) receives it
        rabbitTemplate.convertAndSend(RabbitMQConfig.EXCHANGE_NAME, RabbitMQConfig.ROUTING_KEY, event);
        log.info("Published TransactionCreatedEvent to RabbitMQ for transaction: {} (email={}, account={})",
                transaction.getId(), recipientEmail.isEmpty() ? "<not resolved>" : recipientEmail, accountNumber);

        // Also publish in-memory so the Ledger Service (@EventListener) receives it
        eventPublisher.publishEvent(event);
    }

    private void createAuditEntry(UUID transactionId, String statusBefore, String statusAfter, String reason) {
        TransactionAudit audit = TransactionAudit.builder()
                .transactionId(transactionId)
                .statusBefore(statusBefore)
                .statusAfter(statusAfter)
                .reason(reason)
                .build();

        transactionAuditRepository.save(audit);
    }

    private TransactionResponse mapToResponse(Transaction transaction) {
        return TransactionResponse.builder()
                .id(transaction.getId())
                .fromAccountId(transaction.getFromAccountId())
                .toAccountId(transaction.getToAccountId())
                .type(transaction.getType())
                .amount(transaction.getAmount())
                .status(transaction.getStatus())
                .description(transaction.getDescription())
                .requestId(transaction.getRequestId())
                .createdAt(transaction.getCreatedAt())
                .completedAt(transaction.getCompletedAt())
                .build();
    }
}
