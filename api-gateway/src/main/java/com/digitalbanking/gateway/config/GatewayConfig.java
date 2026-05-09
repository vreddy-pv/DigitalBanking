package com.digitalbanking.gateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayConfig {

    @Bean
    public RouteLocator gatewayRoutes(RouteLocatorBuilder builder) {
        return builder.routes()
                .route("auth-service", r -> r
                        .path("/api/v1/auth/**")
                        .uri("http://auth-service:8001"))
                .route("account-service", r -> r
                        .path("/api/v1/accounts/**")
                        .uri("http://account-service:8002"))
                .route("transaction-service", r -> r
                        .path("/api/v1/transactions/**")
                        .uri("http://transaction-service:8003"))
                .route("ledger-service", r -> r
                        .path("/api/v1/ledger/**")
                        .uri("http://ledger-service:8004"))
                .build();
    }
}
