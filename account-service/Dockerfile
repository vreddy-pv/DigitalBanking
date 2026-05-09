FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy pre-built JAR from local Maven build
COPY account-service/target/account-service-1.0.0.jar app.jar

EXPOSE 8002

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8002/api/v1/accounts/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
