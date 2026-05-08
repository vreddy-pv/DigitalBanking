# Digital Banking Platform - Subagents & Specialized Agents

## 🤖 Subagent Architecture

Specialized agents that perform domain-specific tasks autonomously or semi-autonomously. Each subagent is tailored for a specific responsibility area.

---

## 1. Subagent: Test Executor

**Purpose**: Run test suites, analyze failures, generate reports

**Responsibilities**:
- Execute unit tests across all modules
- Run integration tests with Testcontainers
- Generate coverage reports
- Identify and report failing tests
- Suggest fixes for test failures

**Invocation**:
```bash
# Manual trigger via chat
/test-executor run-unit-tests
/test-executor run-integration-tests
/test-executor generate-coverage-report
```

**Configuration**:
```yaml
# .claude/subagents/test-executor.yaml
name: test-executor
type: testing-specialist
capabilities:
  - maven-test-execution
  - testcontainers-orchestration
  - coverage-analysis
  - test-report-generation
  - test-failure-diagnosis

automation:
  triggers:
    - on: push-to-branch
      branch: main
      action: run-full-test-suite
    
    - on: pull-request
      action: run-modified-tests
    
    - on: scheduled
      cron: "0 2 * * *"  # Daily at 2 AM
      action: run-full-test-suite

commands:
  run-full-test-suite:
    - mvn clean verify -DskipITs=false
    - generate-html-report
    - notify-team-results
  
  run-modified-tests:
    - identify-modified-modules
    - run-tests-in-modules
    - comment-on-pr-results
  
  generate-coverage-report:
    - mvn jacoco:report
    - analyze-coverage
    - flag-low-coverage-modules
```

**Capabilities**:
```
✅ Maven test execution (unit, integration, e2e)
✅ Testcontainers orchestration
✅ Test result parsing and analysis
✅ Coverage calculation and trending
✅ Failure root cause analysis
✅ HTML/JSON report generation
✅ Slack/Email notifications
```

---

## 2. Subagent: Build & Deployment

**Purpose**: Build Docker images, deploy services, manage infrastructure

**Responsibilities**:
- Build all microservices (Maven compilation, Docker packaging)
- Push images to container registry
- Deploy to staging/production environments
- Verify deployment health
- Rollback if needed

**Invocation**:
```bash
/deployment-agent build-all-services
/deployment-agent deploy-to-staging
/deployment-agent deploy-to-production --blue-green
/deployment-agent verify-deployment
/deployment-agent rollback-service auth-service
```

**Configuration**:
```yaml
# .claude/subagents/deployment-agent.yaml
name: deployment-agent
type: infrastructure-specialist
capabilities:
  - maven-build
  - docker-image-build
  - container-registry-push
  - kubernetes-deployment
  - ecs-service-management
  - health-verification
  - deployment-rollback

automation:
  triggers:
    - on: tag-pushed
      pattern: "v*"
      action: build-and-deploy-production
    
    - on: pr-merged
      branch: main
      action: build-and-deploy-staging
    
    - on: manual-approval
      action: deploy-to-production

commands:
  build-all-services:
    - mvn clean package -DskipTests -DskipITs
    - docker-compose build
    - tag-images-with-timestamp
    - push-to-registry
  
  deploy-to-staging:
    - verify-tests-passing
    - build-all-services
    - deploy-to-ecs-staging
    - run-smoke-tests
    - notify-team
  
  deploy-to-production:
    - create-blue-green-deployment
    - deploy-green-environment
    - run-health-checks
    - switch-traffic-to-green
    - monitor-for-errors
    - rollback-if-needed

  verify-deployment:
    - check-container-health
    - verify-all-endpoints-responding
    - run-smoke-tests
    - generate-deployment-report
```

**Capabilities**:
```
✅ Maven clean build
✅ Multi-stage Docker builds
✅ Docker image tagging and versioning
✅ AWS ECR/Docker Registry push
✅ ECS task definition updates
✅ Blue-green deployment orchestration
✅ Health check verification
✅ Smoke test execution
✅ Automatic rollback on failure
✅ Deployment logging and reporting
```

---

## 3. Subagent: Database Administrator

**Purpose**: Manage databases, migrations, backups, and data integrity

**Responsibilities**:
- Run Liquibase migrations
- Create and manage backups
- Monitor database health
- Optimize queries
- Detect and repair inconsistencies

**Invocation**:
```bash
/database-admin run-migrations
/database-admin create-backup
/database-admin restore-backup <snapshot-id>
/database-admin check-data-consistency
/database-admin optimize-indexes
```

**Configuration**:
```yaml
# .claude/subagents/database-admin.yaml
name: database-admin
type: database-specialist
capabilities:
  - liquibase-migration-execution
  - postgresql-backup-restore
  - data-consistency-checking
  - query-performance-analysis
  - index-optimization

automation:
  triggers:
    - on: deployment-pre-production
      action: backup-database
    
    - on: migration-needed
      action: run-migrations-and-verify
    
    - on: scheduled
      cron: "0 1 * * *"  # Daily backup at 1 AM
      action: backup-database

commands:
  run-migrations:
    - validate-migration-files
    - backup-database
    - execute-liquibase-update
    - verify-migration-success
    - rollback-on-failure
  
  create-backup:
    - pg_dump-all-databases
    - compress-backup
    - upload-to-s3
    - verify-backup-integrity
  
  check-data-consistency:
    - verify-foreign-key-constraints
    - validate-double-entry-bookkeeping
    - check-ledger-trial-balance
    - flag-inconsistencies
    - generate-repair-script
  
  optimize-indexes:
    - analyze-slow-queries
    - recommend-indexes
    - create-missing-indexes
    - verify-query-improvements
```

**Capabilities**:
```
✅ Liquibase changelog execution
✅ Schema migration rollback
✅ PostgreSQL backup/restore
✅ Data consistency validation
✅ Foreign key constraint checking
✅ Double-entry bookkeeping verification
✅ Slow query detection
✅ Index optimization
✅ Backup retention management
```

---

## 4. Subagent: Monitoring & Alerting

**Purpose**: Monitor system health, detect anomalies, trigger alerts

**Responsibilities**:
- Collect metrics from services
- Monitor resource utilization
- Detect performance degradation
- Generate dashboards
- Send alerts for anomalies

**Invocation**:
```bash
/monitoring-agent setup-prometheus
/monitoring-agent setup-grafana-dashboards
/monitoring-agent check-system-health
/monitoring-agent analyze-performance-metrics
```

**Configuration**:
```yaml
# .claude/subagents/monitoring-agent.yaml
name: monitoring-agent
type: observability-specialist
capabilities:
  - prometheus-setup
  - grafana-dashboard-creation
  - log-aggregation
  - metrics-collection
  - alert-configuration
  - anomaly-detection

monitoring-targets:
  - auth-service:8001
  - account-service:8002
  - transaction-service:8003
  - ledger-service:8004
  - postgres:5432

metrics:
  - http_request_latency_ms
  - http_request_count
  - http_error_rate
  - database_connection_pool_usage
  - jvm_memory_usage
  - jvm_gc_duration_ms

dashboards:
  - services-overview (request rate, latency, errors)
  - database-health (connections, slow queries)
  - infrastructure (CPU, memory, disk)
  - transaction-flow (deposits, withdrawals, ledger)

alerts:
  critical:
    - service-down (error_rate > 10%)
    - database-unavailable
    - memory-leak-detected (trending up for 30min)
  
  warning:
    - high-latency (P95 > 1s)
    - connection-pool-exhausted (> 80%)
    - disk-space-low (> 85%)
```

**Capabilities**:
```
✅ Prometheus metrics collection
✅ Grafana dashboard creation
✅ Custom metric definitions
✅ Alert rule configuration
✅ Log aggregation (ELK stack)
✅ Performance trend analysis
✅ Anomaly detection
✅ Capacity planning recommendations
```

---

## 5. Subagent: Code Quality Analyzer

**Purpose**: Analyze code, identify issues, suggest improvements

**Responsibilities**:
- Run static code analysis
- Check code style compliance
- Detect security vulnerabilities
- Identify code smells
- Suggest refactoring opportunities

**Invocation**:
```bash
/code-quality-analyzer run-full-analysis
/code-quality-analyzer analyze-coverage
/code-quality-analyzer security-scan
/code-quality-analyzer detect-code-smells
```

**Configuration**:
```yaml
# .claude/subagents/code-quality-analyzer.yaml
name: code-quality-analyzer
type: code-review-specialist
capabilities:
  - static-code-analysis
  - code-coverage-analysis
  - security-vulnerability-scanning
  - code-smell-detection
  - duplicate-code-detection
  - complexity-analysis

automation:
  triggers:
    - on: pull-request
      action: analyze-changed-files
    
    - on: push-to-main
      action: run-full-analysis

analysis-tools:
  - checkstyle (code style)
  - pmd (code smells, complexity)
  - spotbugs (potential bugs)
  - owasp-dependency-check (security)
  - jacoco (code coverage)

quality-gates:
  coverage: ">= 80%"
  duplicated-code: "< 5%"
  critical-issues: "== 0"
  high-issues: "== 0"
  security-vulnerabilities: "== 0"

commands:
  run-full-analysis:
    - mvn clean install pmd:check spotbugs:check
    - mvn jacoco:report
    - mvn dependency-check:check
    - generate-quality-report
    - comment-on-pr
  
  security-scan:
    - owasp-dependency-check
    - sonarqube-analysis
    - trivy-image-scan (for docker)
  
  detect-code-smells:
    - pmd-analysis
    - checkstyle-check
    - complexity-analysis
    - dead-code-detection
```

**Capabilities**:
```
✅ PMD/Checkstyle analysis
✅ SpotBugs static analysis
✅ OWASP dependency check
✅ Code coverage reporting
✅ Cyclomatic complexity analysis
✅ Duplicate code detection
✅ Security vulnerability scanning
✅ PR comment generation
```

---

## 6. Subagent: Documentation Generator

**Purpose**: Generate and update documentation automatically

**Responsibilities**:
- Generate API documentation (OpenAPI/Swagger)
- Update database schema documentation
- Create deployment runbooks
- Generate architecture diagrams
- Keep README up-to-date

**Invocation**:
```bash
/documentation-agent generate-api-docs
/documentation-agent generate-schema-docs
/documentation-agent update-readme
/documentation-agent generate-architecture-diagram
```

**Configuration**:
```yaml
# .claude/subagents/documentation-agent.yaml
name: documentation-agent
type: documentation-specialist
capabilities:
  - openapi-generation
  - swagger-ui-setup
  - database-schema-documentation
  - markdown-generation
  - diagram-generation
  - readme-auto-update

automation:
  triggers:
    - on: api-endpoint-added
      action: regenerate-api-docs
    
    - on: database-migration
      action: regenerate-schema-docs
    
    - on: pull-request-merged
      action: update-docs-and-commit

documentation-targets:
  - api-specification (OpenAPI 3.0)
  - database-schema (SQL + descriptions)
  - deployment-guide (step-by-step)
  - troubleshooting-guide
  - architecture-overview
  - contributing-guide

commands:
  generate-api-docs:
    - extract-endpoints-from-controllers
    - generate-openapi-yaml
    - build-swagger-ui
    - update-README-with-examples
  
  generate-schema-docs:
    - extract-jpa-entities
    - query-database-metadata
    - generate-table-documentation
    - create-erd-diagram
  
  update-readme:
    - query-pom-for-versions
    - check-docker-compose-ports
    - generate-quick-start-section
    - update-service-status
```

**Capabilities**:
```
✅ OpenAPI 3.0 generation
✅ Swagger UI integration
✅ Database schema extraction
✅ ER diagram generation
✅ API example generation
✅ Markdown documentation creation
✅ README auto-update
✅ Changelog generation
```

---

## 7. Subagent: Load Tester

**Purpose**: Run load tests, analyze performance, identify bottlenecks

**Responsibilities**:
- Execute load tests with various scenarios
- Analyze performance metrics
- Identify bottlenecks
- Generate performance reports
- Compare with baseline

**Invocation**:
```bash
/load-tester run-basic-test
/load-tester run-sustained-load
/load-tester run-spike-test
/load-tester compare-with-baseline
```

**Configuration**:
```yaml
# .claude/subagents/load-tester.yaml
name: load-tester
type: performance-specialist
capabilities:
  - jmeter-load-testing
  - gatling-performance-testing
  - metrics-collection
  - bottleneck-detection
  - baseline-comparison

test-scenarios:
  basic-test:
    description: "10 concurrent users, 100 total requests"
    ramp-time: 10s
    duration: 60s
    threads: 10
  
  sustained-load:
    description: "30 concurrent users, 5-minute duration"
    ramp-time: 30s
    duration: 300s
    threads: 30
  
  spike-test:
    description: "Sudden spike from 10 to 100 concurrent users"
    ramp-time: 5s
    duration: 120s
    threads: 100
  
  stress-test:
    description: "Increase load until service fails"
    initial-threads: 50
    increment: 10
    increment-period: 60s
    max-threads: 200

success-criteria:
  throughput: ">= 100 TPS"
  latency-p50: "< 100ms"
  latency-p95: "< 500ms"
  latency-p99: "< 1000ms"
  error-rate: "< 1%"

commands:
  run-basic-test:
    - generate-jmeter-testplan
    - start-monitoring
    - run-jmeter
    - collect-metrics
    - generate-report
  
  run-sustained-load:
    - verify-services-healthy
    - execute-sustained-load-test
    - monitor-resource-usage
    - detect-memory-leaks
    - generate-detailed-report
  
  identify-bottlenecks:
    - profile-application
    - analyze-database-queries
    - check-thread-pool-saturation
    - review-lock-contention
    - generate-optimization-report
```

**Capabilities**:
```
✅ JMeter test plan creation
✅ Gatling performance tests
✅ Concurrent user simulation
✅ Ramp-up and sustained load testing
✅ Spike and stress testing
✅ Metrics collection (latency, throughput, errors)
✅ Bottleneck detection
✅ Baseline comparison
✅ HTML report generation
```

---

## 🔄 Subagent Orchestration

### Example: CI/CD Pipeline Integration

```yaml
# .github/workflows/automated-testing.yml
name: Automated Testing & Quality

on: [push, pull_request]

jobs:
  test-executor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Test Executor Subagent
        run: |
          curl -X POST $CLAUDE_CODE_API \
            -H "Authorization: Bearer $CLAUDE_TOKEN" \
            -d '{"agent": "test-executor", "command": "run-full-test-suite"}'

  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Code Quality Analyzer
        run: |
          curl -X POST $CLAUDE_CODE_API \
            -H "Authorization: Bearer $CLAUDE_TOKEN" \
            -d '{"agent": "code-quality-analyzer", "command": "run-full-analysis"}'

  deployment:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    needs: [test-executor, code-quality]
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Staging
        run: |
          curl -X POST $CLAUDE_CODE_API \
            -H "Authorization: Bearer $CLAUDE_TOKEN" \
            -d '{"agent": "deployment-agent", "command": "deploy-to-staging"}'
```

---

## 📝 Creating New Subagents

### Template
```yaml
name: [agent-name]
type: [specialist-type]
purpose: "[One-line description]"

capabilities:
  - capability-1
  - capability-2
  - capability-3

automation:
  triggers:
    - on: [event-type]
      condition: "[optional condition]"
      action: "[action-to-take]"

commands:
  [action-name]:
    - [step-1]
    - [step-2]
    - [step-3]

integration:
  slack: true
  email: true
  github-comments: true
```

### Best Practices
- One responsibility per subagent
- Clear trigger conditions
- Idempotent operations
- Comprehensive error handling
- Detailed logging and reporting

---

**Next Steps**:
- Integrate subagents with GitHub Actions
- Add Slack notifications for subagent actions
- Create dashboards for subagent activity
- Develop test suite for subagent workflows
