package com.digitalbanking.auth.service;

import com.digitalbanking.auth.dto.AuthResponse;
import com.digitalbanking.auth.dto.LoginRequest;
import com.digitalbanking.auth.dto.RegisterRequest;
import com.digitalbanking.auth.entity.User;
import com.digitalbanking.auth.entity.UserRole;
import com.digitalbanking.auth.repository.UserRepository;
import com.digitalbanking.auth.security.JwtTokenProvider;
import com.digitalbanking.common.exception.AppException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final AuthenticationManager authenticationManager;

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new AppException("USER_ALREADY_EXISTS", "Email is already registered");
        }

        User user = User.builder()
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .fullName(request.getFullName())
                .active(true)
                .build();

        UserRole customerRole = UserRole.builder()
                .roleName("CUSTOMER")
                .user(user)
                .build();

        user.setRoles(List.of(customerRole));
        userRepository.save(user);

        log.info("User registered successfully: {}", request.getEmail());

        return AuthResponse.builder()
                .userId(user.getId())
                .email(user.getEmail())
                .fullName(user.getFullName())
                .roles(List.of("CUSTOMER"))
                .build();
    }

    public AuthResponse login(LoginRequest request) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            request.getEmail(),
                            request.getPassword()
                    )
            );

            User user = userRepository.findByEmail(request.getEmail())
                    .orElseThrow(() -> new AppException("USER_NOT_FOUND", "User not found"));

            String accessToken = jwtTokenProvider.generateAccessToken(authentication);
            String refreshToken = jwtTokenProvider.generateRefreshToken(request.getEmail());

            List<String> roles = user.getRoles() != null
                    ? user.getRoles().stream().map(UserRole::getRoleName).toList()
                    : List.of();

            log.info("User logged in successfully: {}", request.getEmail());

            return AuthResponse.builder()
                    .userId(user.getId())
                    .email(user.getEmail())
                    .fullName(user.getFullName())
                    .accessToken(accessToken)
                    .refreshToken(refreshToken)
                    .roles(roles)
                    .expiresIn(jwtTokenProvider.getExpirationTimeMs() / 1000)
                    .build();

        } catch (Exception e) {
            log.error("Login failed for user: {}", request.getEmail());
            throw new AppException("INVALID_CREDENTIALS", "Invalid email or password");
        }
    }

    public AuthResponse refreshToken(String refreshToken) {
        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new AppException("INVALID_TOKEN", "Invalid or expired refresh token");
        }

        String email = jwtTokenProvider.getEmailFromToken(refreshToken);
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new AppException("USER_NOT_FOUND", "User not found"));

        String newAccessToken = jwtTokenProvider.generateAccessToken(email);

        List<String> roles = user.getRoles() != null
                ? user.getRoles().stream().map(UserRole::getRoleName).toList()
                : List.of();

        return AuthResponse.builder()
                .userId(user.getId())
                .email(user.getEmail())
                .fullName(user.getFullName())
                .accessToken(newAccessToken)
                .roles(roles)
                .expiresIn(jwtTokenProvider.getExpirationTimeMs() / 1000)
                .build();
    }

    public AuthResponse validateToken(String token) {
        if (!jwtTokenProvider.validateToken(token)) {
            throw new AppException("INVALID_TOKEN", "Invalid or expired token");
        }

        String email = jwtTokenProvider.getEmailFromToken(token);
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new AppException("USER_NOT_FOUND", "User not found"));

        List<String> roles = user.getRoles() != null
                ? user.getRoles().stream().map(UserRole::getRoleName).toList()
                : List.of();

        return AuthResponse.builder()
                .userId(user.getId())
                .email(user.getEmail())
                .fullName(user.getFullName())
                .roles(roles)
                .build();
    }
}
