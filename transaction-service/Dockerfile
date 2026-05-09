FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy pre-built JAR from local Maven build
COPY transaction-service/target/transaction-service-1.0.0.jar app.jar

EXPOSE 8003

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8003/api/v1/transactions/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
