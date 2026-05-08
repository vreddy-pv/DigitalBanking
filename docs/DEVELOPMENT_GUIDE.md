# Development Guide - Digital Banking Platform

## Local Setup Instructions

### Prerequisites Installation

#### 1. Java 21
```bash
# Verify installation
java -version

# Should output: openjdk 21.x.x
```

#### 2. Maven 3.9+
```bash
mvn -v

# Should output: Apache Maven 3.9.x
```

#### 3. Docker & Docker Compose
```bash
docker --version
docker-compose --version
```

---

## First Time Setup

### Step 1: Clone Repository
```bash
cd C:\Veera\AI\agents\DigitalBanking
```

### Step 2: Start PostgreSQL
```bash
docker-compose up -d postgres

# Wait for PostgreSQL to be healthy
docker-compose ps

# Should show: postgres - Up (healthy)
```

### Step 3: Build Project
```bash
# Build all modules
mvn clean install -DskipTests

# Output should end with: BUILD SUCCESS
```

### Step 4: Run Tests
```bash
# Unit tests
mvn test

# Integration tests (requires PostgreSQL)
mvn verify

# Should show: Tests run: XX, Failures: 0
```

### Step 5: Start Auth Service
```bash
# Option A: Docker
docker-compose up -d auth-service

# Option B: Local IDE
mvn -pl auth-service spring-boot:run

# Service should be running at: http://localhost:8001
```

### Step 6: Verify Health
```bash
curl http://localhost:8001/api/v1/auth/health

# Response: {"success":true,"data":"Auth Service is running",...}
```

---

## Development Workflow

### Adding New Code

#### 1. Create Feature Branch
```bash
git checkout -b feature/my-feature
```

#### 2. Write Tests First (TDD)
```bash
# Create test file
auth-service/src/test/java/com/digitalbanking/auth/service/MyFeatureTest.java

# Write test class:
@Test
void testMyFeature() {
    // Arrange
    // Act
    // Assert
}
```

#### 3. Implement Feature
```bash
# Create implementation
auth-service/src/main/java/com/digitalbanking/auth/service/MyFeature.java

# Run tests
mvn test

# Run integration tests
mvn verify
```

#### 4. Code Quality
```bash
# Check code style
mvn clean compile

# All tests passing
mvn test

# Coverage report
mvn jacoco:report
# View: auth-service/target/site/jacoco/index.html
```

---

## Running Services Locally

### Option A: Docker Compose (Recommended for Phase 1-2)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f auth-service

# Stop all services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Option B: IDE (IntelliJ/Eclipse)
```bash
# Open each service as separate Maven project
# Run > Edit Configurations > Maven
# Command: spring-boot:run
# Working directory: auth-service
```

### Option C: Command Line
```bash
# Terminal 1: PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  postgres:15-alpine

# Terminal 2: Auth Service
mvn -pl auth-service spring-boot:run

# Terminal 3: Test API
curl http://localhost:8001/api/v1/auth/health
```

---

## Testing

### Unit Tests
```bash
# Run all unit tests
mvn test

# Run specific test class
mvn test -Dtest=AuthServiceTest

# Run specific test method
mvn test -Dtest=AuthServiceTest#testLoginSuccess
```

### Integration Tests
```bash
# Requires PostgreSQL running
mvn verify

# Or run only integration tests
mvn verify -Dgroups=integration

# View test report
# target/surefire-reports/
```

### Test Coverage
```bash
# Generate coverage report
mvn jacoco:report

# View report
# target/site/jacoco/index.html
```

### Manual API Testing

#### Using cURL
```bash
# Register user
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123","fullName":"Test User"}'

# Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}'

# Validate token
TOKEN="<access_token_from_login>"
curl -X POST "http://localhost:8001/api/v1/auth/validate?token=$TOKEN"
```

#### Using Postman
1. Import collection from `docs/Postman_Collection.json` (create this)
2. Set environment variables:
   - `base_url`: http://localhost:8001
   - `access_token`: (automatically set after login)
3. Run requests in sequence

#### Using Python Requests
```python
import requests

BASE_URL = "http://localhost:8001/api/v1/auth"

# Register
response = requests.post(f"{BASE_URL}/register", json={
    "email": "test@example.com",
    "password": "Password123",
    "fullName": "Test User"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/login", json={
    "email": "test@example.com",
    "password": "Password123"
})
data = response.json()
access_token = data['data']['accessToken']
print(f"Token: {access_token}")

# Validate token
response = requests.post(f"{BASE_URL}/validate?token={access_token}")
print(response.json())
```

---

## Database Management

### PostgreSQL Connection
```bash
# Connect to database
docker-compose exec postgres psql -U postgres

# List databases
\l

# Connect to specific database
\c auth_db

# List tables
\dt

# View users table
SELECT * FROM users;

# Exit
\q
```

### Database Migrations (Liquibase)

Migrations are in: `auth-service/src/main/resources/db/changelog/`

#### Creating New Migration
```bash
# Create new changelog file
auth-service/src/main/resources/db/changelog/002-add-feature.yaml

# Add to master changelog
# (update db.changelog-master.yaml to include new file)

# Migration runs automatically on service startup
mvn spring-boot:run
```

#### Rollback
```bash
# Liquibase automatically rolls back on error
# To manually rollback:
mvn liquibase:rollback

# Or revert migration file and restart service
```

### Viewing Schema
```sql
-- Connect to auth_db
\c auth_db

-- View all tables
\dt

-- View users table structure
\d users

-- View indexes
\di

-- View foreign keys
\d+ user_roles
```

---

## Debugging

### Enable Debug Logging
```bash
# Set environment variable
export LOGGING_LEVEL_COM_DIGITALBANKING=DEBUG

# Or modify application.yml:
logging:
  level:
    com.digitalbanking: DEBUG
```

### View Service Logs
```bash
# Docker
docker-compose logs -f auth-service

# Local run (logs in console)
mvn spring-boot:run

# Tail log file
tail -f logs/auth-service.log
```

### Debug Mode in IDE
```bash
# IntelliJ: Run > Debug 'AuthServiceApplication'
# Then: View > Debugging > Debug Console

# Eclipse: Run > Debug Configurations > Java Application
# Set breakpoints and Debug
```

### Common Issues

#### Port Already In Use
```bash
# Find process using port 8001
lsof -i :8001

# Kill process
kill -9 <PID>

# Or change port in application.yml:
server:
  port: 8002
```

#### PostgreSQL Connection Refused
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

#### Liquibase Migration Failed
```bash
# Check Liquibase logs
docker-compose logs auth-service | grep liquibase

# Validate YAML syntax
mvn liquibase:validate

# Manual rollback
docker-compose exec postgres psql -U postgres -d auth_db
DELETE FROM databasechangelog WHERE id='your_changeset_id';
\q

# Restart service
docker-compose restart auth-service
```

#### Tests Failing with Testcontainers
```bash
# Ensure Docker is running
docker ps

# Pull required image
docker pull postgres:15-alpine

# Check Testcontainers config
# ~/.testcontainers.properties

# Run tests with verbose output
mvn test -X
```

---

## Building & Deployment

### Local Build
```bash
# Build JAR for Auth Service
mvn clean package -pl auth-service

# JAR location
auth-service/target/auth-service-1.0.0.jar

# Run JAR directly
java -jar auth-service/target/auth-service-1.0.0.jar
```

### Docker Build
```bash
# Build Docker image
docker build -f auth-service/Dockerfile -t digital-banking-auth:1.0.0 .

# Run Docker image
docker run -p 8001:8001 \
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://host.docker.internal:5432/auth_db \
  -e SPRING_DATASOURCE_USERNAME=postgres \
  -e SPRING_DATASOURCE_PASSWORD=password \
  digital-banking-auth:1.0.0
```

### Docker Compose Build
```bash
# Rebuild image
docker-compose build --no-cache auth-service

# Start with fresh build
docker-compose up --build auth-service
```

---

## IDE Setup

### IntelliJ IDEA
```bash
# 1. Open project: File > Open > select DigitalBanking folder
# 2. Configure SDK: Project Structure > Project > Java 21
# 3. Enable annotations: Settings > Build > Compiler > Annotation Processors > Enable annotation processing
# 4. Configure Run Configuration:
#    Run > Edit Configurations > + Maven
#    Name: Auth Service
#    Command: spring-boot:run
#    Working directory: $PROJECT_DIR$/auth-service
# 5. Run: Shift + F10
```

### VS Code
```bash
# 1. Install extensions:
#    - Extension Pack for Java
#    - Spring Boot Extension Pack
#    - Docker
#
# 2. Open folder: File > Open Folder > select DigitalBanking
#
# 3. Create .vscode/launch.json:
# 4. Debug: Press F5
```

### Eclipse
```bash
# 1. Import project: File > Import > Existing Maven Projects
# 2. Select DigitalBanking folder
# 3. Configure: Right-click project > Properties > Java Build Path
# 4. Run: Run > Run As > Java Application
```

---

## Continuous Integration (Phase 2)

### GitHub Actions (Planned)
```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-java@v2
        with:
          java-version: '21'
      - run: mvn clean verify
      - run: mvn jacoco:report
      - uses: codecov/codecov-action@v2
```

---

## Performance Tuning

### Database Connection Pool
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
```

### JVM Tuning
```bash
# Add JVM options for auth-service
export JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC"

mvn spring-boot:run
```

### Query Optimization
```sql
-- View query performance
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
```

---

## Useful Commands

```bash
# Clean build
mvn clean

# Skip tests
mvn install -DskipTests

# Run specific profile
mvn install -P dev

# View dependency tree
mvn dependency:tree

# Check for outdated dependencies
mvn versions:display-dependency-updates

# Format code
mvn spotless:apply

# Check code style
mvn spotless:check
```

---

## Next Steps

### Week 1 Completion Checklist
- ✅ Local development environment set up
- ✅ Auth Service running
- ✅ Tests passing
- ✅ API endpoints working
- ✅ Database migrations running

### Week 2 Goals
- Start Account Service
- Set up API Gateway routing
- Implement account creation
- Connect to Auth Service

