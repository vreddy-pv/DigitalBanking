# Stage 1: Build
FROM maven:3.9.6-eclipse-temurin-17 AS builder

WORKDIR /app

COPY pom.xml pom.xml
COPY transaction-service/pom.xml transaction-service/
COPY common/pom.xml common/

COPY common/src common/src
COPY transaction-service/src transaction-service/src

RUN mvn clean package -DskipTests -pl transaction-service

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=builder /app/transaction-service/target/transaction-service-1.0.0.jar app.jar

EXPOSE 8003

ENTRYPOINT ["java", "-jar", "app.jar"]
