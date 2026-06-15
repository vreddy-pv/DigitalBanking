FROM eclipse-temurin:17-alpine AS builder

WORKDIR /build

COPY . .

RUN apk add --no-cache maven && \
    mvn clean package -DskipTests -q -pl loan-service -am

FROM eclipse-temurin:17-alpine AS dd-agent
RUN apk add --no-cache curl && \
    curl -fsSL -o /dd-java-agent.jar \
         https://repo1.maven.org/maven2/com/datadoghq/dd-java-agent/1.37.0/dd-java-agent-1.37.0.jar

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY --from=builder /build/loan-service/target/loan-service-1.0.0.jar app.jar
COPY --from=dd-agent /dd-java-agent.jar /dd-java-agent.jar

EXPOSE 8012

HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=60s \
    CMD curl -f http://localhost:8012/api/v1/loans/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
