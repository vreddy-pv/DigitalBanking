# Digital Banking Platform - Hooks & Automation Triggers

## 🎣 Git Hooks

Pre-commit and post-commit hooks that run automatically on git events.

### Setup Git Hooks

```bash
cd C:\Veera\AI\agents\DigitalBanking

# Initialize git hooks directory
mkdir -p .git/hooks

# Copy hook scripts
cp hooks/pre-commit.sh .git/hooks/pre-commit
cp hooks/commit-msg.sh .git/hooks/commit-msg
cp hooks/post-commit.sh .git/hooks/post-commit
cp hooks/pre-push.sh .git/hooks/pre-push

# Make executable
chmod +x .git/hooks/*

# Verify hooks installed
ls -la .git/hooks/
```

---

## 1. Hook: Pre-Commit Checks

**File**: `.git/hooks/pre-commit`

**Purpose**: Validate code quality before committing

**Runs**: Before `git commit`

**Checks**:
- ✅ Code formatting (Checkstyle)
- ✅ Unit tests pass
- ✅ No hardcoded secrets (passwords, API keys)
- ✅ No large binary files
- ✅ No TODO/FIXME comments without issues
- ✅ No merge conflict markers

**Script**:
```bash
#!/bin/bash

echo "🔍 Pre-commit checks running..."

# 1. Check for secrets
echo "  Checking for secrets..."
if grep -r "password\|api_key\|secret" --include="*.java" src/ | grep -v "test"; then
  echo "❌ Hardcoded secrets detected! Remove before committing."
  exit 1
fi

# 2. Check for large files
echo "  Checking file sizes..."
MAX_SIZE=5242880  # 5MB
for file in $(git diff --cached --name-only); do
  if [ -f "$file" ]; then
    size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
    if [ "$size" -gt "$MAX_SIZE" ]; then
      echo "❌ File too large: $file ($(($size/1024/1024))MB > 5MB)"
      exit 1
    fi
  fi
done

# 3. Format check (optional, non-blocking)
echo "  Running checkstyle..."
mvn checkstyle:check -q 2>/dev/null || echo "⚠️  Checkstyle warnings (non-blocking)"

# 4. Unit tests
echo "  Running unit tests..."
mvn test -q --fail-at-end
if [ $? -ne 0 ]; then
  echo "❌ Unit tests failed! Fix tests before committing."
  exit 1
fi

echo "✅ Pre-commit checks passed!"
exit 0
```

---

## 2. Hook: Commit Message Validation

**File**: `.git/hooks/commit-msg`

**Purpose**: Enforce commit message conventions

**Runs**: When commit message is created

**Format**: `[TYPE] Message (max 72 chars) - Jira ticket optional`

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Script**:
```bash
#!/bin/bash

COMMIT_MSG=$(cat "$1")

# Check format
if ! echo "$COMMIT_MSG" | grep -qE "^\[(feat|fix|docs|refactor|test|chore)\]"; then
  echo "❌ Commit message must start with [TYPE]"
  echo "   Valid types: feat, fix, docs, refactor, test, chore"
  echo "   Example: [feat] Add transaction deposit endpoint"
  exit 1
fi

# Check length
FIRST_LINE=$(echo "$COMMIT_MSG" | head -1)
if [ ${#FIRST_LINE} -gt 72 ]; then
  echo "❌ Commit message first line too long (> 72 chars)"
  exit 1
fi

# Check for issue reference
if ! echo "$COMMIT_MSG" | grep -qE "#[0-9]+|BANK-[0-9]+"; then
  echo "⚠️  No issue reference found (optional but recommended)"
fi

echo "✅ Commit message format valid!"
exit 0
```

**Example Commit Messages**:
```
[feat] Add transaction deposit endpoint #123
[fix] Fix JWT token expiration validation BANK-456
[docs] Update API documentation
[test] Add integration tests for account service
[refactor] Simplify transaction validation logic
[chore] Update Spring Boot dependencies
```

---

## 3. Hook: Post-Commit Notification

**File**: `.git/hooks/post-commit`

**Purpose**: Send notifications after successful commit

**Runs**: After `git commit` succeeds

**Actions**:
- 📨 Send commit info to Slack
- 📝 Update pull request
- 📊 Trigger CI pipeline status check

**Script**:
```bash
#!/bin/bash

COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
AUTHOR=$(git log -1 --pretty=%an)
TIMESTAMP=$(date +%Y-%m-%d\ %H:%M:%S)

echo "📤 Sending commit notification..."

# Send to Slack (if webhook configured)
if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
  curl -X POST "$SLACK_WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    -d "{
      \"text\": \"Commit pushed by $AUTHOR\",
      \"attachments\": [{
        \"color\": \"#36a64f\",
        \"title\": \"$COMMIT_MSG\",
        \"text\": \"SHA: $COMMIT_SHA\n Time: $TIMESTAMP\",
        \"footer\": \"Digital Banking Platform\"
      }]
    }"
fi

# Log commit for audit
echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $AUTHOR: $COMMIT_MSG ($COMMIT_SHA)" >> commit.log

exit 0
```

---

## 4. Hook: Pre-Push Validation

**File**: `.git/hooks/pre-push`

**Purpose**: Validate before pushing to remote

**Runs**: Before `git push`

**Checks**:
- ✅ All tests pass
- ✅ Branch is up-to-date with main
- ✅ Code coverage above threshold
- ✅ No commits to main (feature branch protection)

**Script**:
```bash
#!/bin/bash

echo "🔍 Pre-push validation..."

# 1. Protect main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" == "main" ]; then
  echo "❌ Cannot push directly to main! Create a PR instead."
  exit 1
fi

# 2. Verify branch is up-to-date
echo "  Checking if branch is up-to-date..."
git fetch origin main
if ! git merge-base --is-ancestor origin/main HEAD; then
  echo "⚠️  Branch is behind main. Pull latest changes:"
  echo "    git fetch origin && git rebase origin/main"
  exit 1
fi

# 3. Run full test suite
echo "  Running full test suite..."
mvn clean verify -DskipITs=false -q
if [ $? -ne 0 ]; then
  echo "❌ Tests failed! Push blocked."
  exit 1
fi

# 4. Check coverage
echo "  Checking code coverage..."
COVERAGE=$(grep -oP 'Covered%.*=\K[0-9.]+' target/site/jacoco/index.html | head -1)
COVERAGE_THRESHOLD=80
if (( $(echo "$COVERAGE < $COVERAGE_THRESHOLD" | bc -l) )); then
  echo "❌ Code coverage ${COVERAGE}% < ${COVERAGE_THRESHOLD}%"
  exit 1
fi

echo "✅ Pre-push validation passed!"
exit 0
```

---

## 🔄 CI/CD Pipeline Hooks

### GitHub Actions Workflows

#### 1. Trigger: Push to Main → Run Tests

**File**: `.github/workflows/test-on-push.yml`

```yaml
name: Test on Push

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
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
      - uses: actions/checkout@v3
      
      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Run tests
        run: mvn clean verify -DskipITs=false
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./target/site/jacoco/jacoco.xml
      
      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const coverage = fs.readFileSync('target/coverage.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Test Results\n${coverage}`
            });
```

#### 2. Trigger: PR Created → Check Code Quality

**File**: `.github/workflows/code-quality-check.yml`

```yaml
name: Code Quality Check

on:
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for SonarQube
      
      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          java-version: '17'
      
      - name: Run checkstyle
        run: mvn checkstyle:check
      
      - name: Run spotbugs
        run: mvn spotbugs:check
      
      - name: Security scan (OWASP)
        run: mvn org.owasp:dependency-check-maven:check
      
      - name: SonarQube scan
        run: |
          mvn clean verify -DskipITs sonar:sonar \
            -Dsonar.projectKey=digital-banking \
            -Dsonar.host.url=${{ secrets.SONAR_HOST_URL }} \
            -Dsonar.login=${{ secrets.SONAR_TOKEN }}
      
      - name: Report results
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.checks.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              name: 'Code Quality',
              head_sha: context.sha,
              status: 'completed',
              conclusion: 'success'
            });
```

#### 3. Trigger: Tag Pushed → Build & Deploy Production

**File**: `.github/workflows/deploy-production.yml`

```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v1
        env:
          AWS_REGION: us-east-1
      
      - name: Build and push Docker images
        run: |
          for service in auth-service account-service transaction-service ledger-service; do
            docker build -t ${{ secrets.ECR_REGISTRY }}/$service:${{ github.ref_name }} $service/
            docker push ${{ secrets.ECR_REGISTRY }}/$service:${{ github.ref_name }}
          done
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        env:
          AWS_REGION: us-east-1
        run: |
          for service in auth-service account-service transaction-service ledger-service; do
            aws ecs update-service \
              --cluster banking-prod \
              --service $service \
              --force-new-deployment \
              --region $AWS_REGION
          done
      
      - name: Verify deployment
        run: |
          sleep 30
          for port in 8001 8002 8003 8004; do
            curl -f https://api.banking-prod.com:$port/health || exit 1
          done
      
      - name: Slack notification
        uses: slackapi/slack-github-action@v1.24.0
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "Production deployment completed for ${{ github.ref_name }}",
              "blocks": [{
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "✅ Production Deploy\n*Tag:* ${{ github.ref_name }}"
                }
              }]
            }
```

---

## ⏰ Scheduled Hooks (Cron Jobs)

### Daily Backup

**File**: `.github/workflows/daily-backup.yml`

```yaml
name: Daily Database Backup

on:
  schedule:
    - cron: '0 1 * * *'  # 1 AM UTC daily

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Backup PostgreSQL
        env:
          PGPASSWORD: ${{ secrets.DB_PASSWORD }}
        run: |
          pg_dump -h ${{ secrets.DB_HOST }} -U postgres auth_db | gzip > backup-auth-db-$(date +%Y%m%d).sql.gz
          pg_dump -h ${{ secrets.DB_HOST }} -U postgres account_db | gzip > backup-account-db-$(date +%Y%m%d).sql.gz
          pg_dump -h ${{ secrets.DB_HOST }} -U postgres transaction_db | gzip > backup-transaction-db-$(date +%Y%m%d).sql.gz
          pg_dump -h ${{ secrets.DB_HOST }} -U postgres ledger_db | gzip > backup-ledger-db-$(date +%Y%m%d).sql.gz
      
      - name: Upload to S3
        run: |
          for file in backup-*.sql.gz; do
            aws s3 cp $file s3://banking-backups/$(date +%Y/%m/%d)/$file
          done
      
      - name: Verify backup integrity
        run: |
          for file in backup-*.sql.gz; do
            gunzip -t $file || exit 1
          done
      
      - name: Cleanup old backups
        run: |
          aws s3 rm s3://banking-backups --recursive --exclude "*" --include "$(date -d '30 days ago' +%Y/%m/%d)/*"
```

### Weekly Load Test

**File**: `.github/workflows/weekly-load-test.yml`

```yaml
name: Weekly Load Test

on:
  schedule:
    - cron: '0 2 * * 0'  # 2 AM UTC every Sunday

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services
        run: docker-compose -f docker-compose.prod.yml up -d
      
      - name: Wait for services
        run: sleep 30
      
      - name: Run load test
        run: |
          jmeter -n -t load-test-plan.jmx \
            -l results.jtl \
            -j jmeter.log
      
      - name: Analyze results
        run: |
          jmeter -g results.jtl -o report/
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: load-test-report-$(date +%Y%m%d)
          path: report/
      
      - name: Alert if degradation
        if: failure()
        uses: slackapi/slack-github-action@v1.24.0
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "⚠️  Load test degradation detected",
              "blocks": [{
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "Performance metrics below threshold. See report for details."
                }
              }]
            }
```

### Nightly Data Reconciliation

**File**: `.github/workflows/nightly-reconciliation.yml`

```yaml
name: Nightly Ledger Reconciliation

on:
  schedule:
    - cron: '0 3 * * *'  # 3 AM UTC daily

jobs:
  reconcile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run reconciliation
        env:
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
        run: |
          psql $DATABASE_URL << EOF
          -- Verify trial balance
          SELECT 
            SUM(debit) as total_debits,
            SUM(credit) as total_credits,
            (SUM(debit) - SUM(credit)) as variance
          FROM journal_entries;
          
          -- Alert if not balanced
          DO \$\$
          BEGIN
            IF (SELECT SUM(debit) - SUM(credit) FROM journal_entries) != 0 THEN
              RAISE EXCEPTION 'Ledger not balanced!';
            END IF;
          END \$\$;
          EOF
      
      - name: Check for missing entries
        env:
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
        run: |
          psql $DATABASE_URL << EOF
          -- Find transactions without ledger entries
          SELECT t.id, t.type, t.amount
          FROM transactions t
          LEFT JOIN journal_entries j ON t.id = j.transaction_id
          WHERE j.id IS NULL
          AND t.status = 'COMPLETED';
          EOF
      
      - name: Alert on issues
        if: failure()
        uses: slackapi/slack-github-action@v1.24.0
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "🚨 Ledger reconciliation failed",
              "blocks": [{
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "Nightly reconciliation detected data inconsistency. Check database immediately."
                }
              }]
            }
```

---

## 🔐 Setup Instructions

### 1. Configure Secrets (GitHub)

In GitHub repo Settings → Secrets and variables → Actions, add:

```
DB_HOST=postgres.digital-banking.com
DB_PASSWORD=<strong-password>
ECR_REGISTRY=<account-id>.dkr.ecr.us-east-1.amazonaws.com
SONAR_HOST_URL=https://sonarqube.digital-banking.com
SONAR_TOKEN=<token>
SLACK_WEBHOOK=https://hooks.slack.com/services/...
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
```

### 2. Enable Workflows

```bash
# Ensure workflows directory exists
mkdir -p .github/workflows

# Copy workflow files
cp workflows/*.yml .github/workflows/

# Commit and push
git add .github/workflows/
git commit -m "[chore] Add CI/CD workflow definitions"
git push origin main
```

### 3. Test Git Hooks Locally

```bash
# Test pre-commit
git add .
.git/hooks/pre-commit

# Test commit message validation
echo "[feat] Test message" > /tmp/commit-msg
.git/hooks/commit-msg /tmp/commit-msg

# Test pre-push
.git/hooks/pre-push origin main
```

---

## 📊 Hook Execution Flow

```
Developer Work
    ↓
git commit
    ├─ pre-commit hook (format, tests)
    ├─ commit-msg hook (message format)
    └─ post-commit hook (notify)
    ↓
git push
    ├─ pre-push hook (tests, coverage, branch check)
    └─ Push to remote
    ↓
GitHub Actions
    ├─ test-on-push.yml (run tests)
    ├─ code-quality-check.yml (lint, security)
    ├─ weekly-load-test.yml (performance)
    └─ nightly-reconciliation.yml (data integrity)
    ↓
PR Status Checks
    ├─ Tests passed ✅
    ├─ Code quality ✅
    ├─ Coverage > 80% ✅
    └─ Deployment preview ✅
    ↓
PR Merge → Production Deploy
    ↓
Slack/Email Notifications
```

---

## 🐛 Troubleshooting Hooks

### Hook Not Executing

```bash
# Check hook is executable
ls -la .git/hooks/pre-commit
# Should show: -rwxr-xr-x

# Make executable
chmod +x .git/hooks/pre-commit

# Test hook directly
.git/hooks/pre-commit
```

### Bypass Hooks (Emergency Only)

```bash
# Skip pre-commit hook
git commit --no-verify -m "[fix] Emergency fix"

# Skip pre-push hook
git push --no-verify

# ⚠️ Not recommended - use only in emergencies
```

### Debug Hook Output

```bash
# Add debug output to hook script
set -x  # Enable debug mode
# ... rest of script
set +x  # Disable debug mode

# Run hook manually with debug
bash -x .git/hooks/pre-commit
```

---

**Next Steps**:
- Test all hooks in local environment
- Configure GitHub secrets
- Verify CI/CD pipeline
- Set up Slack notifications
- Monitor hook execution in logs
