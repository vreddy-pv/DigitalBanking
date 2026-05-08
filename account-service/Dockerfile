# Stage 1: Build
FROM maven:3.9.6-eclipse-temurin-17 AS builder

WORKDIR /app

COPY pom.xml pom.xml
COPY account-service/pom.xml account-service/
COPY common/pom.xml common/

COPY common/src common/src
COPY account-service/src account-service/src

RUN mvn clean package -DskipTests -pl account-service

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=builder /app/account-service/target/account-service-1.0.0.jar app.jar

EXPOSE 8002

ENTRYPOINT ["java", "-jar", "app.jar"]
