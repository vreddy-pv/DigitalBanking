# Stage 1: Build
FROM maven:3.9.6-eclipse-temurin-17 AS builder

WORKDIR /app

COPY pom.xml pom.xml
COPY ledger-service/pom.xml ledger-service/
COPY transaction-service/pom.xml transaction-service/
COPY common/pom.xml common/

COPY common/src common/src
COPY transaction-service/src transaction-service/src
COPY ledger-service/src ledger-service/src

RUN mvn clean package -DskipTests -pl ledger-service

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=builder /app/ledger-service/target/ledger-service-1.0.0.jar app.jar

EXPOSE 8004

ENTRYPOINT ["java", "-jar", "app.jar"]
