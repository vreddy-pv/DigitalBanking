package com.digitalbanking.gateway.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.web.server.SecurityWebFilterChain;

@Configuration
@EnableWebFluxSecurity
public class SecurityConfig {

    @Bean
    public SecurityWebFilterChain springSecurityFilterChain(ServerHttpSecurity http) {
        http
            // Disable CSRF for stateless API gateway
            .csrf(csrf -> csrf.disable())
            // Allow all requests (authentication is delegated to backend services)
            .authorizeExchange(authz -> authz.anyExchange().permitAll());

        return http.build();
    }
}
