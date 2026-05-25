FROM eclipse-temurin:17-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY settings.xml ./
COPY common ./common
COPY ai-bid-gateway ./ai-bid-gateway
COPY ai-bid-user ./ai-bid-user
COPY ai-bid-project ./ai-bid-project
COPY ai-bid-material ./ai-bid-material
COPY ai-bid-document ./ai-bid-document
RUN mvn clean package -DskipTests -pl ai-bid-document -am

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/ai-bid-document/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
