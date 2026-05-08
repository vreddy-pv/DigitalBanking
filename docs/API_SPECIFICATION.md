# Digital Banking Platform - API Specification

**Version**: 1.0.0  
**Last Updated**: 2026-05-08  
**Status**: Phase 1 (Auth Service Complete)

## Table of Contents
1. [Authentication API](#authentication-api)
2. [Error Handling](#error-handling)
3. [Rate Limiting](#rate-limiting)
4. [Security](#security)

---

## Authentication API

### Base URL
```
http://localhost:8001/api/v1/auth
```

### 1. Register User

**Endpoint**: `POST /register`

**Description**: Register a new user account

**Request Headers**:
```http
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "fullName": "John Doe"
}
```

**Validation Rules**:
- `email`: Required, must be valid email format, unique in system
- `password`: Required, minimum 8 characters, maximum 100
- `fullName`: Required, 2-255 characters

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "fullName": "John Doe",
    "roles": ["CUSTOMER"]
  },
  "message": "User registered successfully",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Response** (400 Bad Request - Duplicate Email):
```json
{
  "success": false,
  "code": "USER_ALREADY_EXISTS",
  "message": "Email is already registered",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Response** (400 Bad Request - Validation Error):
```json
{
  "success": false,
  "code": "VALIDATION_ERROR",
  "message": "Input validation failed",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "fullName": "John Doe"
  }'
```

---

### 2. Login

**Endpoint**: `POST /login`

**Description**: Authenticate user and receive JWT tokens

**Request Headers**:
```http
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Validation Rules**:
- `email`: Required, valid email format
- `password`: Required, non-empty

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "fullName": "John Doe",
    "accessToken": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNjE2MjM5MDIyLCJleHAiOjE2MTYyMzk2MjIsInJvbGVzIjpbIkNVU1RPTUVSIl19.signature",
    "refreshToken": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNjE2MjM5MDIyLCJleHAiOjE2MTY4NDMwMjJ9.signature",
    "roles": ["CUSTOMER"],
    "expiresIn": 900
  },
  "message": "Login successful",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Token Details**:
- `accessToken`: Valid for 15 minutes (900 seconds)
- `refreshToken`: Valid for 7 days (604800 seconds)
- JWT Algorithm: HS512 (HMAC with SHA-512)

**Response** (400 Bad Request - Invalid Credentials):
```json
{
  "success": false,
  "code": "INVALID_CREDENTIALS",
  "message": "Invalid email or password",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

---

### 3. Validate Token

**Endpoint**: `POST /validate`

**Description**: Validate a JWT token and return user information

**Request Headers**:
```http
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `token` (string, required): JWT token to validate

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "fullName": "John Doe",
    "roles": ["CUSTOMER"]
  },
  "message": "Token is valid",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Response** (400 Bad Request - Invalid Token):
```json
{
  "success": false,
  "code": "INVALID_TOKEN",
  "message": "Invalid or expired token",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Example cURL**:
```bash
curl -X POST "http://localhost:8001/api/v1/auth/validate?token=eyJhbGciOiJIUzUxMiJ9..."
```

---

### 4. Refresh Token

**Endpoint**: `POST /refresh-token`

**Description**: Refresh an expired access token using a valid refresh token

**Query Parameters**:
- `refreshToken` (string, required): Valid refresh token

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "fullName": "John Doe",
    "accessToken": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNjE2MjM5MDIyLCJleHAiOjE2MTYyMzk2MjIsInJvbGVzIjpbIkNVU1RPTUVSIl19.signature",
    "roles": ["CUSTOMER"],
    "expiresIn": 900
  },
  "message": "Token refreshed successfully",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Response** (400 Bad Request - Invalid Refresh Token):
```json
{
  "success": false,
  "code": "INVALID_TOKEN",
  "message": "Invalid or expired refresh token",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Example cURL**:
```bash
curl -X POST "http://localhost:8001/api/v1/auth/refresh-token?refreshToken=eyJhbGciOiJIUzUxMiJ9..."
```

---

### 5. Health Check

**Endpoint**: `GET /health`

**Description**: Verify Auth Service is running

**Response** (200 OK):
```json
{
  "success": true,
  "data": "Auth Service is running",
  "message": "Health check passed",
  "timestamp": "2026-05-08T10:30:00"
}
```

**Example cURL**:
```bash
curl http://localhost:8001/api/v1/auth/health
```

---

## Error Handling

### Error Response Format
All errors follow this standard format:

```json
{
  "success": false,
  "code": "ERROR_CODE",
  "message": "Human-readable error message",
  "transactionId": "unique-transaction-id (optional)",
  "timestamp": "2026-05-08T10:30:00"
}
```

### HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | OK | Successful operation |
| 201 | Created | User registered successfully |
| 400 | Bad Request | Invalid input, user already exists |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | User doesn't have permission |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Unexpected server error |

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `USER_ALREADY_EXISTS` | 400 | Email is already registered |
| `INVALID_CREDENTIALS` | 400 | Email or password is incorrect |
| `USER_NOT_FOUND` | 404 | User doesn't exist |
| `INVALID_TOKEN` | 400 | Token is invalid or expired |
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected error |

---

## Rate Limiting

**Phase 1**: No rate limiting (development scale)

**Phase 2** (Planned):
- 100 requests per minute per IP
- 1000 requests per minute per authenticated user
- X-RateLimit headers included in responses

---

## Security

### JWT Token Structure

Tokens are signed using HS512 (HMAC with SHA-512)

**Header**:
```json
{
  "alg": "HS512",
  "typ": "JWT"
}
```

**Payload (Access Token)**:
```json
{
  "sub": "user@example.com",
  "iat": 1616239022,
  "exp": 1616239922,
  "roles": ["CUSTOMER"]
}
```

**Payload (Refresh Token)**:
```json
{
  "sub": "user@example.com",
  "iat": 1616239022,
  "exp": 1616843022
}
```

### Password Security
- Algorithm: BCrypt (Spring Security default)
- Work Factor: 12 (configurable)
- Minimum Length: 8 characters
- No special character requirements (Phase 1)

### HTTPS
- **Phase 1**: Not required (localhost development)
- **Phase 3**: Mandatory in production

### CORS
- **Phase 1**: No CORS restrictions
- **Phase 2**: Configure cross-origin policies

---

## API Usage Examples

### Complete Login Flow

```bash
# 1. Register
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123",
    "fullName": "New User"
  }'

# Response includes: userId, email, fullName, roles

# 2. Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123"
  }'

# Response includes: accessToken, refreshToken, expiresIn

# 3. Use Access Token (for future service calls)
curl -X GET http://localhost:8002/api/v1/accounts \
  -H "Authorization: Bearer <accessToken>"

# 4. When access token expires, refresh it
curl -X POST "http://localhost:8001/api/v1/auth/refresh-token?refreshToken=<refreshToken>"

# 5. Get new access token
# Repeat step 3 with new token
```

---

## OpenAPI/Swagger Integration (Phase 2)

API documentation will be available at:
```
http://localhost:8001/swagger-ui.html
```

---

## Versioning

Current API version: `v1`

Future versions will use URL path versioning:
- `/api/v1/` (current)
- `/api/v2/` (future)

---

## Future Endpoints (Phase 2-3)

### Account Service
- `POST /api/v1/accounts/register` - Create account
- `GET /api/v1/accounts/{accountId}` - Get account details
- `PUT /api/v1/accounts/{accountId}/profile` - Update profile

### Transaction Service
- `POST /api/v1/transactions/deposit` - Deposit money
- `POST /api/v1/transactions/withdraw` - Withdraw money
- `POST /api/v1/transactions/transfer` - Transfer to another account

### Ledger Service
- `GET /api/v1/ledger/accounts` - List GL accounts
- `GET /api/v1/ledger/trial-balance` - Trial balance report

