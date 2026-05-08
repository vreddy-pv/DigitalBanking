FROM maven:3.9.6-eclipse-temurin-21 AS builder
WORKDIR /build

# Copy parent pom
COPY pom.xml ./
COPY common ./common
COPY auth-service ./auth-service

# Build
RUN mvn clean package -DskipTests -am -pl auth-service

# Runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

COPY --from=builder /build/auth-service/target/auth-service-1.0.0.jar app.jar

EXPOSE 8001

ENTRYPOINT ["java", "-jar", "app.jar"]
