FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy pre-built JAR from local Maven build
COPY ledger-service/target/ledger-service-1.0.0.jar app.jar

EXPOSE 8004

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8004/api/v1/ledger/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
