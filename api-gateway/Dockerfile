FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Copy pre-built JAR from local Maven build
COPY api-gateway/target/api-gateway-1.0.0.jar app.jar

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
