package com.digitalbanking.transaction.service;

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
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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
        TransactionCreatedEvent event = TransactionCreatedEvent.builder()
                .transactionId(transaction.getId())
                .fromAccountId(transaction.getFromAccountId())
                .toAccountId(transaction.getToAccountId())
                .type(transaction.getType())
                .amount(transaction.getAmount())
                .description(transaction.getDescription())
                .timestamp(System.currentTimeMillis())
                .build();

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
