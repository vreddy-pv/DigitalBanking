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
# Stage 2: Runtime - Run the built application
# ==============================================================================
FROM eclipse-temurin:17-jre-alpine

RUN apk add --no-cache curl

WORKDIR /app

# Copy only the built JAR from builder stage
COPY --from=builder /build/customer-service/target/customer-service-1.0.0.jar app.jar

EXPOSE 8005

ENTRYPOINT ["java", "-jar", "app.jar"]
