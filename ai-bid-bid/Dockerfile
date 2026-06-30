FROM eclipse-temurin:17 AS builder
RUN apt-get update && apt-get install -y maven && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# Copy entire project for multi-module Maven build
COPY pom.xml .
COPY settings.xml /root/.m2/settings.xml
COPY common/common-core ./common/common-core
COPY common/common-security ./common/common-security
COPY ai-bid-gateway ./ai-bid-gateway
COPY ai-bid-user ./ai-bid-user
COPY ai-bid-project ./ai-bid-project
COPY ai-bid-material ./ai-bid-material
COPY ai-bid-bid ./ai-bid-bid
COPY ai-bid-document ./ai-bid-document
RUN mvn clean package -DskipTests -pl ai-bid-bid -am

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/ai-bid-bid/target/*.jar app.jar
EXPOSE 8085
ENTRYPOINT ["java", "-jar", "app.jar"]
