FROM eclipse-temurin:17-alpine AS builder

WORKDIR /build

COPY . .

RUN apk add --no-cache maven && \
    mvn clean package -DskipTests -q -pl ops-service -am

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY --from=builder /build/ops-service/target/ops-service-1.0.0.jar app.jar

EXPOSE 8013

HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=60s \
    CMD curl -f http://localhost:8013/api/v1/ops/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
