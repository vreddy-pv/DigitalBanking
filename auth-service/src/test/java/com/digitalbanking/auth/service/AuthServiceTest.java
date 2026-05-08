package com.digitalbanking.auth.service;

import com.digitalbanking.auth.dto.AuthResponse;
import com.digitalbanking.auth.dto.LoginRequest;
import com.digitalbanking.auth.dto.RegisterRequest;
import com.digitalbanking.auth.entity.User;
import com.digitalbanking.auth.entity.UserRole;
import com.digitalbanking.auth.repository.UserRepository;
import com.digitalbanking.auth.security.JwtTokenProvider;
import com.digitalbanking.common.exception.AppException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtTokenProvider jwtTokenProvider;

    @Mock
    private AuthenticationManager authenticationManager;

    @InjectMocks
    private AuthService authService;

    private RegisterRequest registerRequest;
    private LoginRequest loginRequest;
    private User testUser;

    @BeforeEach
    void setUp() {
        registerRequest = RegisterRequest.builder()
                .email("test@example.com")
                .password("password123")
                .fullName("Test User")
                .build();

        loginRequest = LoginRequest.builder()
                .email("test@example.com")
                .password("password123")
                .build();

        UserRole role = UserRole.builder()
                .roleName("CUSTOMER")
                .build();

        testUser = User.builder()
                .id(UUID.randomUUID())
                .email("test@example.com")
                .passwordHash("hashed_password")
                .fullName("Test User")
                .active(true)
                .roles(List.of(role))
                .build();
    }

    @Test
    void testRegisterSuccess() {
        when(userRepository.existsByEmail(registerRequest.getEmail())).thenReturn(false);
        when(passwordEncoder.encode(registerRequest.getPassword())).thenReturn("hashed_password");
        when(userRepository.save(any(User.class))).thenReturn(testUser);

        AuthResponse response = authService.register(registerRequest);

        assertNotNull(response);
        assertEquals("test@example.com", response.getEmail());
        assertEquals("Test User", response.getFullName());
        assertTrue(response.getRoles().contains("CUSTOMER"));

        verify(userRepository).save(any(User.class));
    }

    @Test
    void testRegisterDuplicateEmail() {
        when(userRepository.existsByEmail(registerRequest.getEmail())).thenReturn(true);

        AppException exception = assertThrows(AppException.class, () ->
                authService.register(registerRequest)
        );

        assertEquals("USER_ALREADY_EXISTS", exception.getCode());
    }

    @Test
    void testLoginSuccess() {
        Authentication auth = new UsernamePasswordAuthenticationToken("test@example.com", "password123");
        when(authenticationManager.authenticate(any())).thenReturn(auth);
        when(userRepository.findByEmail(loginRequest.getEmail())).thenReturn(Optional.of(testUser));
        when(jwtTokenProvider.generateAccessToken(auth)).thenReturn("access_token");
        when(jwtTokenProvider.generateRefreshToken("test@example.com")).thenReturn("refresh_token");
        when(jwtTokenProvider.getExpirationTimeMs()).thenReturn(900000L);

        AuthResponse response = authService.login(loginRequest);

        assertNotNull(response);
        assertEquals("test@example.com", response.getEmail());
        assertEquals("access_token", response.getAccessToken());
        assertEquals("refresh_token", response.getRefreshToken());

        verify(authenticationManager).authenticate(any());
    }

    @Test
    void testLoginInvalidCredentials() {
        when(authenticationManager.authenticate(any())).thenThrow(new RuntimeException("Bad credentials"));

        AppException exception = assertThrows(AppException.class, () ->
                authService.login(loginRequest)
        );

        assertEquals("INVALID_CREDENTIALS", exception.getCode());
    }

    @Test
    void testValidateTokenSuccess() {
        when(jwtTokenProvider.validateToken("valid_token")).thenReturn(true);
        when(jwtTokenProvider.getEmailFromToken("valid_token")).thenReturn("test@example.com");
        when(userRepository.findByEmail("test@example.com")).thenReturn(Optional.of(testUser));

        AuthResponse response = authService.validateToken("valid_token");

        assertNotNull(response);
        assertEquals("test@example.com", response.getEmail());
    }

    @Test
    void testValidateTokenInvalid() {
        when(jwtTokenProvider.validateToken("invalid_token")).thenReturn(false);

        AppException exception = assertThrows(AppException.class, () ->
                authService.validateToken("invalid_token")
        );

        assertEquals("INVALID_TOKEN", exception.getCode());
    }
}
