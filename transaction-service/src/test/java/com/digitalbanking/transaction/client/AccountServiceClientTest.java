package com.digitalbanking.transaction.client;

import com.digitalbanking.transaction.client.AccountServiceClient.AccountData;
import com.digitalbanking.transaction.client.AccountServiceClient.CustomerData;
import org.junit.jupiter.api.Test;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Unit tests for AccountServiceClient.
 *
 * Because the JSON wrapper response classes are private records inside
 * AccountServiceClient, the success path is covered by integration tests
 * (where a real HTTP response is deserialized).  Here we focus on the
 * graceful-degradation contract: every error must return Optional.empty()
 * without propagating an exception to the caller.
 *
 * ThrowingRestTemplate simulates connection failures and timeouts by always
 * throwing ResourceAccessException, which exercises the catch-all in both
 * getAccountById and getCustomerById.
 */
class AccountServiceClientTest {

    private static final String BASE_URL = "http://account-service:8002";

    // -----------------------------------------------------------------------
    // getAccountById — error/degradation paths
    // -----------------------------------------------------------------------

    @Test
    void getAccountById_returnsEmpty_onConnectionRefused() {
        AccountServiceClient client = new AccountServiceClient(
                new ThrowingRestTemplate("Connection refused"), BASE_URL);

        Optional<AccountData> result = client.getAccountById(UUID.randomUUID());

        assertThat(result).isEmpty();
    }

    @Test
    void getAccountById_returnsEmpty_onTimeout() {
        AccountServiceClient client = new AccountServiceClient(
                new ThrowingRestTemplate("Read timed out"), BASE_URL);

        Optional<AccountData> result = client.getAccountById(UUID.randomUUID());

        assertThat(result).isEmpty();
    }

    @Test
    void getAccountById_returnsEmpty_onNetworkError() {
        AccountServiceClient client = new AccountServiceClient(
                new ThrowingRestTemplate("Network unreachable"), BASE_URL);

        assertThat(client.getAccountById(UUID.randomUUID())).isEmpty();
    }

    // -----------------------------------------------------------------------
    // getCustomerById — error/degradation paths
    // -----------------------------------------------------------------------

    @Test
    void getCustomerById_returnsEmpty_onConnectionRefused() {
        AccountServiceClient client = new AccountServiceClient(
                new ThrowingRestTemplate("Connection refused"), BASE_URL);

        Optional<CustomerData> result = client.getCustomerById(UUID.randomUUID());

        assertThat(result).isEmpty();
    }

    @Test
    void getCustomerById_returnsEmpty_onTimeout() {
        AccountServiceClient client = new AccountServiceClient(
                new ThrowingRestTemplate("Read timed out"), BASE_URL);

        Optional<CustomerData> result = client.getCustomerById(UUID.randomUUID());

        assertThat(result).isEmpty();
    }

    @Test
    void getCustomerById_returnsEmpty_onNetworkError() {
        AccountServiceClient client = new AccountServiceClient(
                new ThrowingRestTemplate("Network unreachable"), BASE_URL);

        assertThat(client.getCustomerById(UUID.randomUUID())).isEmpty();
    }

    // -----------------------------------------------------------------------
    // Helper: RestTemplate that always throws ResourceAccessException
    // -----------------------------------------------------------------------

    private static class ThrowingRestTemplate extends RestTemplate {
        private final String message;

        ThrowingRestTemplate(String message) {
            this.message = message;
        }

        @Override
        public <T> T getForObject(String url, Class<T> responseType, Object... uriVariables) {
            throw new ResourceAccessException(message);
        }
    }
}
