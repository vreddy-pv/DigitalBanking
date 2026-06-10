FROM eclipse-temurin:17-alpine AS builder

WORKDIR /build

COPY . .

RUN apk add --no-cache maven && \
    mvn clean package -DskipTests -q -pl complaint-service -am

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY --from=builder /build/complaint-service/target/complaint-service-1.0.0.jar app.jar

EXPOSE 8011

HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=60s \
    CMD curl -f http://localhost:8011/api/v1/complaints/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
