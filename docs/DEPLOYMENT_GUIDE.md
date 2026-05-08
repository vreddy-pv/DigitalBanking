# Digital Banking Platform - Deployment Guide

## 🚀 Deployment Overview

This guide covers deploying the Digital Banking MVP across three environments: **Development**, **Staging**, and **Production**.

## 📋 Prerequisites

### Local Development
- Docker 20.10+
- Docker Compose 2.0+
- Java 17 JDK
- Maven 3.9+
- Git

### Staging/Production
- AWS Account (EC2, RDS, ECS)
- Docker Registry (ECR)
- CI/CD Pipeline (GitHub Actions)
- PostgreSQL 15+
- Monitoring Stack (Prometheus, Grafana)

---

## 🖥️ Local Development Deployment

### Step 1: Clone Repository
```bash
cd C:\Veera\AI\agents\DigitalBanking
git clone <repo-url> .
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env with local values
# JWT_SECRET=<your-secret>
# DATABASE_PASSWORD=<password>
```

### Step 3: Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Expected output:
# CONTAINER ID    IMAGE              STATUS
# ...postgres...  postgres:15-alpine  Up 2 minutes (healthy)
# ...auth-svc...  auth-service...     Up 1 minute (healthy)
# ...account-svc..account-service.   Up 1 minute (healthy)
# ...trans-svc...transaction-service Up 1 minute (healthy)
# ...ledger-svc...ledger-service...  Up 1 minute (healthy)
```

### Step 4: Run Tests
```bash
# Unit tests (all modules)
mvn test

# Integration tests (requires PostgreSQL)
mvn verify

# Expected: BUILD SUCCESS
```

### Step 5: Verify Services
```bash
# Auth Service
curl http://localhost:8001/api/v1/auth/health

# Account Service
curl http://localhost:8002/api/v1/accounts/health

# Transaction Service
curl http://localhost:8003/api/v1/transactions/health

# Ledger Service
curl http://localhost:8004/api/v1/ledger/health

# Expected response for each:
# {"success":true,"data":"Service is running"}
```

### Step 6: View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service

# Last 100 lines
docker-compose logs --tail=100 auth-service
```

---

## 🔧 Staging Deployment (AWS)

### Architecture
```
Load Balancer (ALB)
    ↓
ECS Cluster (3 AZs)
├─ Auth Service (2 tasks)
├─ Account Service (2 tasks)
├─ Transaction Service (2 tasks)
└─ Ledger Service (2 tasks)
    ↓
RDS PostgreSQL (Multi-AZ)
```

### Step 1: Build & Push Docker Images

```bash
# Build all images
mvn clean package -DskipTests

# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push each service
REGISTRY=<account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t $REGISTRY/auth-service:latest auth-service/
docker push $REGISTRY/auth-service:latest

# Repeat for account-service, transaction-service, ledger-service
```

### Step 2: Create RDS PostgreSQL Instances

```bash
# Staging RDS (Single-AZ for cost)
aws rds create-db-instance \
  --db-instance-identifier digital-banking-staging \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username postgres \
  --master-user-password <strong-password> \
  --allocated-storage 20 \
  --publicly-accessible false \
  --vpc-security-group-ids sg-xxxxxxxx

# Create databases
psql -h <rds-endpoint> -U postgres -c "CREATE DATABASE auth_db;"
psql -h <rds-endpoint> -U postgres -c "CREATE DATABASE account_db;"
psql -h <rds-endpoint> -U postgres -c "CREATE DATABASE transaction_db;"
psql -h <rds-endpoint> -U postgres -c "CREATE DATABASE ledger_db;"
```

### Step 3: Deploy to ECS

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name banking-staging

# Register task definitions (one per service)
aws ecs register-task-definition --cli-input-json file://auth-service-task-def.json
aws ecs register-task-definition --cli-input-json file://account-service-task-def.json
# ... repeat for other services

# Create ECS services
aws ecs create-service \
  --cluster banking-staging \
  --service-name auth-service \
  --task-definition auth-service:1 \
  --desired-count 2 \
  --launch-type EC2
```

### Step 4: Configure Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name banking-alb \
  --subnets subnet-xxx subnet-yyy

# Create target groups
aws elbv2 create-target-group \
  --name auth-service \
  --protocol HTTP \
  --port 8001

# Create listener rules
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80
```

### Step 5: Enable Auto-Scaling

```bash
# Create scaling policy
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name banking-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://target-tracking-config.json
```

### Step 6: Set Up Monitoring

```bash
# CloudWatch Alarms
aws cloudwatch put-metric-alarm \
  --alarm-name auth-service-high-latency \
  --metric-name Latency \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold

# Enable detailed monitoring
aws logs create-log-group --log-group-name /ecs/banking
```

---

## 🔐 Production Deployment (AWS)

### Architecture
```
CloudFront (CDN)
    ↓
API Gateway (Rate Limiting, Auth)
    ↓
ALB (Multi-AZ)
    ↓
ECS Cluster (Multi-AZ, Auto-Scaling)
├─ Auth Service (4 tasks across 3 AZs)
├─ Account Service (4 tasks across 3 AZs)
├─ Transaction Service (4 tasks across 3 AZs)
└─ Ledger Service (4 tasks across 3 AZs)
    ↓
RDS PostgreSQL (Multi-AZ, Read Replicas)
    ↓
ElastiCache Redis (Multi-AZ)
```

### Pre-Deployment Checklist

- [ ] Code review and merged to main
- [ ] All tests passing (coverage > 80%)
- [ ] Security audit completed
- [ ] Load testing verified (100+ TPS capacity)
- [ ] Runbooks created for incidents
- [ ] Backup & disaster recovery tested
- [ ] Monitoring and alerting configured
- [ ] SSL/TLS certificates issued
- [ ] Environment variables secured in AWS Secrets Manager

### Step 1: Blue-Green Deployment

```bash
# Keep old version running (Blue)
# Deploy new version to separate infrastructure (Green)
# Test Green environment thoroughly
# Switch traffic from Blue to Green
# Keep Blue as rollback point for 24 hours

# Create new task definition (v2)
aws ecs register-task-definition \
  --family auth-service \
  --container-definitions file://auth-service-v2.json

# Update service to new task definition
aws ecs update-service \
  --cluster banking-prod \
  --service auth-service \
  --task-definition auth-service:2 \
  --force-new-deployment

# Verify deployment successful
aws ecs describe-services \
  --cluster banking-prod \
  --services auth-service \
  --query 'services[0].deployments'

# Expected: Both PRIMARY (v1) and ACTIVE (v2) deployments exist
# Once v2 is healthy, deactivate v1
```

### Step 2: Database Migrations

```bash
# Pre-production testing
liquibase --changeLogFile=db.changelog-master.yaml update-sql
# Review SQL changes

# Backup production database
aws rds create-db-snapshot \
  --db-instance-identifier banking-prod \
  --db-snapshot-identifier banking-prod-$(date +%Y%m%d-%H%M%S)

# Apply migrations (during maintenance window)
liquibase --changeLogFile=db.changelog-master.yaml update

# Verify migrations
SELECT * FROM databasechangelog;
```

### Step 3: Health Checks & Smoke Tests

```bash
# Run smoke tests against production
curl -X GET https://api.banking-prod.com/api/v1/auth/health \
  -H "Authorization: Bearer $PROD_TOKEN"

curl -X POST https://api.banking-prod.com/api/v1/accounts/health \
  -H "Authorization: Bearer $PROD_TOKEN"

# Verify all services responding
for service in auth account transaction ledger; do
  status=$(curl -s -o /dev/null -w "%{http_code}" \
    https://api.banking-prod.com/api/v1/$service/health)
  echo "$service: $status"
  # Expected: 200
done
```

### Step 4: Canary Deployment (Phase 3)

```bash
# Route 5% of traffic to new version
aws elbv2 modify-listener \
  --listener-arn arn:... \
  --default-actions file://canary-routing.json

# Monitor metrics for 1 hour
CloudWatch Metrics:
- Error rate (target: < 0.1%)
- P95 latency (target: < 500ms)
- CPU utilization (target: < 70%)

# If metrics acceptable, increase to 50%, then 100%
```

---

## 🔄 Continuous Deployment (CI/CD)

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:  # Manual trigger

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '17'
      - run: mvn test verify --batch-mode
      
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          registry: ${{ secrets.ECR_REGISTRY }}
          username: AWS
          password: ${{ secrets.ECR_PASSWORD }}
      - uses: docker/build-push-action@v4
        with:
          context: auth-service
          push: true
          tags: ${{ secrets.ECR_REGISTRY }}/auth-service:${{ github.sha }}
          
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to ECS
        env:
          AWS_REGION: us-east-1
        run: |
          aws ecs update-service \
            --cluster banking-prod \
            --service auth-service \
            --force-new-deployment \
            --region $AWS_REGION
```

---

## 🛠️ Rollback Procedure

### Immediate Rollback (If Critical Issue)

```bash
# 1. Identify affected service
# 2. Switch back to previous task definition version
aws ecs update-service \
  --cluster banking-prod \
  --service auth-service \
  --task-definition auth-service:1  # Previous version

# 3. Force new deployment
aws ecs update-service \
  --cluster banking-prod \
  --service auth-service \
  --force-new-deployment

# 4. Verify old version active
aws ecs describe-services \
  --cluster banking-prod \
  --services auth-service \
  --query 'services[0].deployments[0].taskDefinition'

# 5. Investigation
# - Check CloudWatch logs
# - Review recent changes
# - Post-incident review
```

### Database Rollback

```bash
# If migrations caused issues
# 1. Restore from backup
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier banking-prod-restored \
  --db-snapshot-identifier banking-prod-<timestamp>

# 2. Switch DNS to restored instance
# 3. Verify data integrity
# 4. Post-incident analysis
```

---

## 📊 Monitoring & Alerts

### CloudWatch Dashboards

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "AWS/ApplicationELB", "TargetResponseTime" ],
          [ ".", "HealthyHostCount" ],
          [ ".", "UnHealthyHostCount" ],
          [ "AWS/ECS", "CPUUtilization" ],
          [ ".", "MemoryUtilization" ]
        ],
        "period": 60,
        "stat": "Average",
        "region": "us-east-1"
      }
    }
  ]
}
```

### Critical Alerts

```
1. Service Down (HTTP 5xx > 10/min)
   → Page on-call engineer

2. Latency High (P95 > 1s)
   → Create incident, investigate

3. Database Connection Pool Exhausted
   → Scale up RDS read replicas

4. Disk Space Low (> 80%)
   → Expand RDS storage

5. Memory Leak Detected (Trending up)
   → Restart service, investigate code
```

---

## 📝 Operational Runbooks

### Incident: Database Becomes Unresponsive

```
1. Check RDS metrics (CPU, connections)
2. If locked queries: Kill long-running queries
   SELECT pg_terminate_backend(pid) 
   FROM pg_stat_activity 
   WHERE state = 'active' AND query_start < NOW() - '1 hour'::interval;
   
3. If high memory: Scale up RDS instance
4. If replication lag: Promote read replica
5. If still unresponsive: Failover to standby
6. Contact AWS support if issue persists
```

### Incident: Service Deployment Stuck

```
1. Check ECS task status
   aws ecs describe-tasks --cluster banking-prod --tasks <task-arn>
   
2. If health check failing: Check service logs
   docker logs <container-id>
   
3. If resource constrained: Scale ECS cluster
4. If image pull failing: Check ECR, verify credentials
5. If still stuck: Force new deployment
   aws ecs update-service --cluster banking-prod \
     --service auth-service --force-new-deployment
```

### Incident: Unusual Transaction Activity

```
1. Check Ledger Service logs for errors
2. Verify trial balance: SELECT SUM(debit) = SUM(credit)
3. Query transactions by account for anomalies
4. Check if event processing lagged
5. If data corrupted: Restore from backup and replay events
```

---

## 🔐 Security in Production

### Network Security
- VPC with private subnets for databases
- Security groups restricting inbound traffic
- VPN for admin access
- No public database access

### Secrets Management
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name /banking/prod/jwt-secret \
  --secret-string <jwt-secret>

# Reference in ECS task definition
"secrets": [
  {
    "name": "JWT_SECRET",
    "valueFrom": "arn:aws:secretsmanager:..."
  }
]
```

### Encryption
- **In Transit**: TLS 1.2+ for all APIs
- **At Rest**: RDS encryption enabled
- **Database**: Column-level encryption for PII (Phase 3)

### Compliance
- [ ] PCI-DSS validation
- [ ] SOC 2 audit
- [ ] Data residency requirements
- [ ] Audit logging enabled

---

## 📚 Additional Resources

- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/)
- [PostgreSQL Replication](https://www.postgresql.org/docs/current/warm-standby.html)
- [Blue-Green Deployments](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Liquibase Documentation](https://docs.liquibase.com/)

---

**Next Steps**: 
- Set up automated deployment pipeline
- Implement comprehensive monitoring
- Conduct load testing before production release
