package com.digitalbanking.ledger.service;

import com.digitalbanking.ledger.dto.GLAccountResponse;
import com.digitalbanking.ledger.dto.JournalEntryResponse;
import com.digitalbanking.ledger.entity.GLAccount;
import com.digitalbanking.ledger.entity.JournalEntry;
import com.digitalbanking.ledger.repository.GLAccountRepository;
import com.digitalbanking.ledger.repository.JournalEntryRepository;
import com.digitalbanking.common.exception.AppException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class LedgerService {

    private final GLAccountRepository glAccountRepository;
    private final JournalEntryRepository journalEntryRepository;

    public void initializeGLAccounts() {
        if (glAccountRepository.existsByCode("1000")) {
            log.info("GL accounts already initialized");
            return;
        }

        GLAccount assetsAccount = GLAccount.builder()
                .code("1000")
                .name("Bank Accounts - Assets")
                .type("ASSET")
                .balance(BigDecimal.ZERO)
                .build();

        GLAccount liabilitiesAccount = GLAccount.builder()
                .code("2000")
                .name("Customer Deposits - Liabilities")
                .type("LIABILITY")
                .balance(BigDecimal.ZERO)
                .build();

        glAccountRepository.save(assetsAccount);
        glAccountRepository.save(liabilitiesAccount);

        log.info("GL accounts initialized");
    }

    public void createJournalEntries(UUID transactionId, String type, BigDecimal amount,
                                     UUID fromAccountId, UUID toAccountId) {
        GLAccount assetsAccount = glAccountRepository.findByCode("1000")
                .orElseThrow(() -> new AppException("GL_ACCOUNT_NOT_FOUND", "Assets GL account not found", transactionId.toString()));

        GLAccount liabilitiesAccount = glAccountRepository.findByCode("2000")
                .orElseThrow(() -> new AppException("GL_ACCOUNT_NOT_FOUND", "Liabilities GL account not found", transactionId.toString()));

        if ("DEPOSIT".equals(type)) {
            createDebitEntry(transactionId, assetsAccount, amount);
            createCreditEntry(transactionId, liabilitiesAccount, amount);

            assetsAccount.setBalance(assetsAccount.getBalance().add(amount));
            liabilitiesAccount.setBalance(liabilitiesAccount.getBalance().add(amount));
        } else if ("WITHDRAWAL".equals(type)) {
            createCreditEntry(transactionId, assetsAccount, amount);
            createDebitEntry(transactionId, liabilitiesAccount, amount);

            assetsAccount.setBalance(assetsAccount.getBalance().subtract(amount));
            liabilitiesAccount.setBalance(liabilitiesAccount.getBalance().subtract(amount));
        } else if ("TRANSFER".equals(type)) {
            createJournalEntry(transactionId, assetsAccount, amount, null);
            createJournalEntry(transactionId, assetsAccount, null, amount);
        }

        glAccountRepository.save(assetsAccount);
        glAccountRepository.save(liabilitiesAccount);

        log.info("Journal entries created for transaction: {} with type: {}", transactionId, type);
    }

    public List<JournalEntryResponse> getJournalEntriesByTransaction(UUID transactionId) {
        List<JournalEntry> entries = journalEntryRepository.findByTransactionId(transactionId);
        return entries.stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    public GLAccountResponse getGLAccountBalance(UUID accountId) {
        GLAccount account = glAccountRepository.findById(accountId)
                .orElseThrow(() -> new AppException("GL_ACCOUNT_NOT_FOUND", "GL account not found", accountId.toString()));

        return mapToGLAccountResponse(account);
    }

    public List<GLAccountResponse> getAllGLAccounts() {
        List<GLAccount> accounts = glAccountRepository.findAll();
        return accounts.stream()
                .map(this::mapToGLAccountResponse)
                .collect(Collectors.toList());
    }

    public String getTrialBalance() {
        List<GLAccount> accounts = glAccountRepository.findAll();

        BigDecimal totalDebits = BigDecimal.ZERO;
        BigDecimal totalCredits = BigDecimal.ZERO;

        for (GLAccount account : accounts) {
            if ("ASSET".equals(account.getType())) {
                totalDebits = totalDebits.add(account.getBalance());
            } else if ("LIABILITY".equals(account.getType())) {
                totalCredits = totalCredits.add(account.getBalance());
            }
        }

        boolean balanced = totalDebits.compareTo(totalCredits) == 0;
        String result = String.format("Total Debits: %s, Total Credits: %s, Balanced: %s",
                totalDebits, totalCredits, balanced);

        log.info("Trial balance: {}", result);

        return result;
    }

    private void createDebitEntry(UUID transactionId, GLAccount account, BigDecimal amount) {
        createJournalEntry(transactionId, account, amount, null);
    }

    private void createCreditEntry(UUID transactionId, GLAccount account, BigDecimal amount) {
        createJournalEntry(transactionId, account, null, amount);
    }

    private void createJournalEntry(UUID transactionId, GLAccount account, BigDecimal debit, BigDecimal credit) {
        JournalEntry entry = JournalEntry.builder()
                .transactionId(transactionId)
                .glAccountId(account.getId())
                .debit(debit)
                .credit(credit)
                .build();

        journalEntryRepository.save(entry);
    }

    private JournalEntryResponse mapToResponse(JournalEntry entry) {
        return JournalEntryResponse.builder()
                .id(entry.getId())
                .transactionId(entry.getTransactionId())
                .glAccountId(entry.getGlAccountId())
                .debit(entry.getDebit())
                .credit(entry.getCredit())
                .timestamp(entry.getTimestamp())
                .build();
    }

    private GLAccountResponse mapToGLAccountResponse(GLAccount account) {
        return GLAccountResponse.builder()
                .id(account.getId())
                .code(account.getCode())
                .name(account.getName())
                .type(account.getType())
                .balance(account.getBalance())
                .createdAt(account.getCreatedAt())
                .updatedAt(account.getUpdatedAt())
                .build();
    }
}
