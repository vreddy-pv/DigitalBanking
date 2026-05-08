package com.digitalbanking.common.exception;

public class AppException extends RuntimeException {
    private final String code;
    private final String transactionId;

    public AppException(String code, String message) {
        super(message);
        this.code = code;
        this.transactionId = null;
    }

    public AppException(String code, String message, Throwable cause) {
        super(message, cause);
        this.code = code;
        this.transactionId = null;
    }

    public AppException(String code, String message, String transactionId) {
        super(message);
        this.code = code;
        this.transactionId = transactionId;
    }

    public String getCode() {
        return code;
    }

    public String getTransactionId() {
        return transactionId;
    }
}
