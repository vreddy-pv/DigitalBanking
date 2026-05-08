# Digital Banking Platform - Troubleshooting Guide

## 🔍 Common Issues & Solutions

### Build & Compilation Issues

#### ❌ Error: Maven Build Fails - Module Not Found
```
[ERROR] Failed to execute goal on project auth-service: Could not resolve 
dependencies for project com.digitalbanking:auth-service
```

**Causes**:
1. Missing parent POM in module pom.xml
2. Incorrect module path in root pom.xml
3. Local Maven cache corrupted

**Solutions**:
```bash
# 1. Clear Maven cache and rebuild
mvn clean install -U

# 2. Verify module paths (root pom.xml)
<modules>
  <module>common</module>
  <module>auth-service</module>
  <!-- ... -->
</modules>

# 3. Check parent reference in module pom.xml
<parent>
  <groupId>com.digitalbanking</groupId>
  <artifactId>digital-banking</artifactId>
  <version>1.0.0</version>
  <relativePath>../pom.xml</relativePath>
</parent>

# 4. If still failing, rebuild Maven cache
rm -rf ~/.m2/repository
mvn clean install
```

---

#### ❌ Error: Java Version Mismatch
```
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.x
[ERROR] Source option 21 is not supported. Use 17 or less.
```

**Cause**: pom.xml configured for Java 21 but only Java 17 available

**Solution**:
```xml
<!-- In root pom.xml <properties> section -->
<properties>
  <java.version>17</java.version>  <!-- Change from 21 to 17 -->
</properties>

# Then rebuild
mvn clean install
```

---

#### ❌ Error: JWT Library API Mismatch
```
[ERROR] Cannot find symbol: method setSubject(String)
```

**Cause**: JJWT library version changed API (0.12.x vs 0.11.x)

**Solution**:
```xml
<!-- Ensure correct version in common pom.xml -->
<dependency>
  <groupId>io.jsonwebtoken</groupId>
  <artifactId>jjwt</artifactId>
  <version>0.11.5</version>  <!-- NOT 0.12.3 -->
</dependency>
<dependency>
  <groupId>io.jsonwebtoken</groupId>
  <artifactId>jjwt-impl</artifactId>
  <version>0.11.5</version>
  <scope>runtime</scope>
</dependency>
<dependency>
  <groupId>io.jsonwebtoken</groupId>
  <artifactId>jjwt-jackson</artifactId>
  <version>0.11.5</version>
  <scope>runtime</scope>
</dependency>
```

**Correct API Usage** (0.11.5):
```java
// ✅ Correct
Date expiryDate = new Date(System.currentTimeMillis() + expirationMs);
Key signingKey = Keys.hmacShaKeyFor(decodedKey);

String token = Jwts.builder()
    .setSubject(email)           // setSubject() not setValue()
    .setIssuedAt(new Date())
    .setExpiration(expiryDate)
    .signWith(signingKey, SignatureAlgorithm.HS512)
    .compact();

// ❌ Wrong (0.12.x syntax)
JwtBuilder builder = Jwts.builder();
builder.subject(email);  // NOT setSubject()
```

---

### Docker & Container Issues

#### ❌ Error: Docker Compose Services Fail to Start
```
ERROR: for postgres  Cannot connect to the Docker daemon
ERROR: Couldn't connect to Docker daemon at http+unix:///var/run/docker.sock
```

**Cause**: Docker daemon not running

**Solutions**:
```bash
# 1. Check if Docker is running
docker ps

# 2. On Windows, start Docker Desktop
# Click Docker Desktop icon in taskbar

# 3. On Linux, start daemon
sudo systemctl start docker
sudo systemctl enable docker

# 4. Verify Docker is working
docker run hello-world
```

---

#### ❌ Error: Service Containers Unhealthy
```
postgres       unhealthy (timeout)
auth-service   unhealthy (timeout)
```

**Cause**: Health check script failing, service startup too slow

**Diagnosis**:
```bash
# Check service logs
docker-compose logs postgres
docker-compose logs auth-service

# Check health check command
docker-compose ps

# Test health check manually
docker-compose exec postgres pg_isready -U postgres
```

**Solutions**:

1. **PostgreSQL health check timeout**:
```yaml
# In docker-compose.yml, increase timeout
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s      # ← Increase from 5s to 10s if slow machine
  retries: 5       # ← Increase retries from 5 to 10
```

2. **Service startup slow**:
```bash
# Increase startup delay
docker-compose up -d
sleep 15  # Give services time to initialize
docker-compose ps
```

3. **Port already in use**:
```bash
# Find process using port
netstat -ano | findstr :8001  # Windows
lsof -i :8001                 # Linux/Mac

# Kill process or change port in docker-compose.yml
kill -9 <PID>
# OR
# Change port: 8001:8001 → 9001:8001
```

---

#### ❌ Error: Can't Connect to Service from Local Machine
```
curl: (7) Failed to connect to localhost:8001
```

**Cause**: Service container not exposing port correctly

**Diagnosis**:
```bash
# Check port mapping
docker-compose ps
# Should show: 0.0.0.0:8001->8001/tcp

# Check if service is listening
docker-compose exec auth-service netstat -tuln | grep 8001

# Check service logs
docker-compose logs auth-service | grep "Tomcat started"
```

**Solutions**:
```bash
# 1. Ensure port is exposed in docker-compose.yml
services:
  auth-service:
    ports:
      - "8001:8001"  # host:container

# 2. Verify service is listening inside container
docker-compose exec auth-service curl localhost:8001/api/v1/auth/health

# 3. Check firewall rules
# Windows Defender: Allow Docker through firewall
# Linux: sudo ufw allow 8001/tcp

# 4. Restart services
docker-compose down
docker-compose up -d
```

---

### Database Issues

#### ❌ Error: Database Connection Refused
```
org.postgresql.util.PSQLException: Connection to localhost:5432 refused
```

**Cause**: PostgreSQL service not running or not accessible

**Diagnosis**:
```bash
# Check if PostgreSQL container is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Test PostgreSQL connection
psql -h localhost -U postgres -c "SELECT 1"

# Or via Docker
docker-compose exec postgres psql -U postgres -c "SELECT 1"
```

**Solutions**:
```bash
# 1. Start PostgreSQL
docker-compose up -d postgres
sleep 10  # Wait for initialization

# 2. Verify databases exist
docker-compose exec postgres psql -U postgres -c "\l"
# Should show: auth_db, account_db, transaction_db, ledger_db

# 3. If databases missing, create them
docker-compose exec postgres psql -U postgres << EOF
CREATE DATABASE auth_db;
CREATE DATABASE account_db;
CREATE DATABASE transaction_db;
CREATE DATABASE ledger_db;
EOF

# 4. Check auth_db has tables
docker-compose exec postgres psql -U postgres -d auth_db -c "\dt"
# Should show: users, user_roles
```

---

#### ❌ Error: Liquibase Migrations Failed
```
[ERROR] Migration failed. Reason: Couldn't acquire change log lock.
```

**Cause**: Stale change log lock in database

**Solutions**:
```bash
# 1. Check if migration is stuck
docker-compose exec postgres psql -U postgres -d auth_db << EOF
SELECT * FROM databasechangeloglock;
EOF

# 2. Clear stuck lock
docker-compose exec postgres psql -U postgres -d auth_db << EOF
UPDATE databasechangeloglock SET LOCKED = FALSE;
EOF

# 3. Retry migration
mvn -pl auth-service liquibase:update

# 4. If still stuck, drop and recreate (DEV ONLY!)
docker-compose exec postgres psql -U postgres -d auth_db << EOF
DROP TABLE IF EXISTS databasechangelog;
DROP TABLE IF EXISTS databasechangeloglock;
EOF
# Then rebuild service
docker-compose down
docker-compose up -d
```

---

#### ❌ Error: Constraint Violation
```
ERROR: duplicate key value violates unique constraint "users_email_key"
```

**Cause**: Trying to insert duplicate email address

**Diagnosis**:
```bash
# Check existing data
docker-compose exec postgres psql -U postgres -d auth_db << EOF
SELECT COUNT(*), email FROM users GROUP BY email HAVING COUNT(*) > 1;
EOF
```

**Solutions**:
```bash
# 1. Use different email
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "unique-email@example.com",
    "password": "Password123",
    "fullName": "Test User"
  }'

# 2. Or clear test data (DEV ONLY!)
docker-compose exec postgres psql -U postgres -d auth_db << EOF
DELETE FROM user_roles;
DELETE FROM users;
EOF
```

---

### Application Runtime Issues

#### ❌ Error: 401 Unauthorized on Protected Endpoints
```
HTTP/1.1 401 Unauthorized
{"code":"INVALID_TOKEN","message":"Token is invalid or expired"}
```

**Cause**: Invalid, expired, or missing JWT token

**Diagnosis**:
```bash
# 1. Verify token is included in request
curl -v http://localhost:8001/api/v1/accounts/123 \
  -H "Authorization: Bearer <token>"

# 2. Verify token format (should be "Bearer <token>")

# 3. Check token expiration
# Decode JWT at jwt.io (for testing only!)
# Check 'exp' claim timestamp
```

**Solutions**:
```bash
# 1. Get valid token via login
LOGIN_RESPONSE=$(curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.accessToken')

# 2. Use token in subsequent requests
curl http://localhost:8001/api/v1/auth/validate \
  -H "Authorization: Bearer $TOKEN"

# 3. If token expired, refresh it
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.refreshToken')

curl -X POST "http://localhost:8001/api/v1/auth/refresh-token?refreshToken=$REFRESH_TOKEN"
```

---

#### ❌ Error: 400 Bad Request - Validation Failed
```
HTTP/1.1 400 Bad Request
{
  "code": "VALIDATION_ERROR",
  "message": "Validation failed",
  "errors": {
    "email": "must be a valid email address",
    "password": "size must be between 8 and 100"
  }
}
```

**Cause**: Request payload doesn't match validation constraints

**Diagnosis**:
```bash
# Check request body
# Validate against documented constraints:
# - email: must be valid email format
# - password: 8-100 characters
# - fullName: 2-255 characters
```

**Solutions**:
```bash
# Valid registration request
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "valid.email@example.com",
    "password": "SecurePassword123",
    "fullName": "John Doe"
  }'

# Invalid requests that will fail:
# 1. Email format
-d '{"email": "invalid-email", ...}'  # Missing @ domain

# 2. Password too short
-d '{"password": "Pass1", ...}'  # Only 5 chars

# 3. Name too short
-d '{"fullName": "J", ...}'  # Only 1 char
```

---

#### ❌ Error: 500 Internal Server Error
```
HTTP/1.1 500 Internal Server Error
{"code":"INTERNAL_ERROR","message":"An unexpected error occurred"}
```

**Cause**: Unhandled exception in application code

**Diagnosis**:
```bash
# 1. Check service logs for stack trace
docker-compose logs auth-service | tail -50

# 2. Enable debug logging
# Add to application.yml:
# logging:
#   level:
#     com.digitalbanking: DEBUG

# 3. Restart with debug logging enabled
docker-compose down
docker-compose up -d
```

**Common Root Causes**:
```
1. Database connection pool exhausted
   → Solution: Check for connection leaks in code, increase pool size

2. NullPointerException in business logic
   → Solution: Add null checks, validate request data

3. Constraint violation (e.g., foreign key)
   → Solution: Verify data relationships before INSERT/UPDATE

4. Timeout talking to another service
   → Solution: Check if other service is running, increase timeout
```

---

### Testing Issues

#### ❌ Error: Integration Tests Fail - Testcontainers
```
com.github.dockerjava.api.exception.NotFoundException: 
  Status 404: {"message":"No such image: postgres:15-alpine"}
```

**Cause**: Docker image not available locally

**Solutions**:
```bash
# 1. Pre-pull the image
docker pull postgres:15-alpine

# 2. If Docker daemon not accessible
docker run hello-world  # Verify Docker works

# 3. If Testcontainers can't find Docker socket
# Set Docker host environment variable (Linux)
export DOCKER_HOST=unix:///var/run/docker.sock

# 4. Run integration tests again
mvn verify
```

---

#### ❌ Error: Test Flakiness - Random Failures
```
Test results: PASSED once, FAILED later, PASSED again
```

**Cause**: Race conditions, timing issues, or resource contention

**Solutions**:
```bash
# 1. Run tests sequentially instead of parallel
mvn test -T 1

# 2. Increase timeouts in integration tests
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
    .withStartupTimeout(Duration.ofSeconds(60));  // Increase from 30s

# 3. Add explicit waits
Thread.sleep(500);  // Wait for async operations

# 4. Check for shared state between tests
@DirtiesContext  // Reset context between tests
public class AuthServiceTest { ... }
```

---

### Performance & Load Issues

#### ❌ Issue: Slow Response Times
```
POST /api/v1/auth/login takes 5+ seconds
```

**Diagnosis**:
```bash
# 1. Monitor database query time
# Add logging to SQL queries:
logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE

# 2. Check database connection pool stats
# Enable metrics in Spring Boot
management:
  endpoints:
    web:
      exposure:
        include: metrics

# 3. Monitor JVM memory usage
jps -l  # List Java processes
jstat -gc <pid> 1000  # GC stats every 1000ms
```

**Common Causes & Solutions**:
```
1. BCrypt password hashing (100-200ms per hash)
   → Expected behavior, acceptable latency

2. Database query without index
   → Add index on frequently queried columns
   CREATE INDEX idx_users_email ON users(email);

3. Connection pool exhausted
   → Increase pool size in application.yml:
   spring.datasource.hikari.maximum-pool-size: 20

4. Slow network latency
   → Verify services on same Docker network
   networks: [banking-network]
```

---

#### ❌ Issue: High Memory Usage / OOM Error
```
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
```

**Diagnosis**:
```bash
# 1. Monitor heap usage
docker stats auth-service  # Shows memory usage

# 2. Generate heap dump
docker exec auth-service jmap -dump:live,format=b,file=/tmp/heap.bin 1

# 3. Analyze with MAT (Memory Analyzer Tool)
```

**Solutions**:
```bash
# 1. Increase JVM heap size
# Add JAVA_OPTS to docker-compose.yml
environment:
  JAVA_OPTS: "-Xmx512m -Xms256m"  # Heap: min 256MB, max 512MB

# 2. Check for memory leaks in code
# Profile application with JProfiler/YourKit

# 3. Monitor object allocations
# Add to application.yml:
management:
  endpoints:
    web:
      exposure:
        include: heapdump
# Then access: http://localhost:8001/actuator/heapdump
```

---

## 🔗 Quick Reference

### Useful Commands

```bash
# Docker
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # Watch logs
docker-compose exec <svc> bash   # Shell into container

# PostgreSQL
psql -h localhost -U postgres     # Connect to DB
\l                                # List databases
\dt                               # List tables
\d <table>                        # Describe table

# Maven
mvn clean install                 # Full rebuild
mvn test                          # Run unit tests
mvn verify                        # Run integration tests
mvn spring-boot:run               # Run service locally

# Curl
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123"}'
```

### Log Levels

```
TRACE  - Very detailed, useful for debugging
DEBUG  - Diagnostic information
INFO   - General informational messages
WARN   - Warning conditions, recoverable
ERROR  - Error conditions, service may be degraded
FATAL  - Severe errors, service likely down
```

---

**Still Stuck?** Check:
1. Service logs: `docker-compose logs -f <service>`
2. Health endpoints: `curl http://localhost:8001/api/v1/auth/health`
3. Database tables: `docker-compose exec postgres psql -U postgres -d auth_db -c "\dt"`
4. Architecture docs: `docs/ARCHITECTURE.md`

