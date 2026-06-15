# ==============================================================================
# Stage 1: Builder - Compile and build with Maven
# ==============================================================================
FROM eclipse-temurin:17-alpine AS builder

WORKDIR /build

# Copy entire project
COPY . .

# Build the project with Maven (skipping tests for faster build)
RUN apk add --no-cache maven && \
    mvn clean package -DskipTests -q

# ==============================================================================
# Stage 2: Datadog Java agent download
# ==============================================================================
FROM eclipse-temurin:17-alpine AS dd-agent
RUN apk add --no-cache curl && \
    curl -fsSL -o /dd-java-agent.jar \
         https://repo1.maven.org/maven2/com/datadoghq/dd-java-agent/1.37.0/dd-java-agent-1.37.0.jar

# ==============================================================================
# Stage 3: Runtime - Run the built application
# ==============================================================================
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY --from=builder /build/ledger-service/target/ledger-service-1.0.0.jar app.jar
COPY --from=dd-agent /dd-java-agent.jar /dd-java-agent.jar

EXPOSE 8004

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8004/api/v1/ledger/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
