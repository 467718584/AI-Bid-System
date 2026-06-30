$content = @"
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: ai-bid-postgres
    environment:
      POSTGRES_DB: ai_bid
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    networks:
      - bid-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ai-bid-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - bid-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  ai-bid-knowledge:
    build:
      context: ./ai-bid-knowledge
      dockerfile: Dockerfile
    container_name: ai-bid-knowledge
    ports:
      - "8086:8086"
    environment:
      - PYTHONUNBUFFERED=1
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_bid
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - bid-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8086/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ai-bid-ai:
    build:
      context: ./ai-bid-ai
      dockerfile: Dockerfile
    container_name: ai-bid-ai
    ports:
      - "8087:8087"
    environment:
      - PYTHONUNBUFFERED=1
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_bid
      - KNOWLEDGE_SERVICE_URL=http://ai-bid-knowledge:8086
    depends_on:
      postgres:
        condition: service_healthy
      ai-bid-knowledge:
        condition: service_healthy
    networks:
      - bid-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8087/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ai-bid-gateway:
    build:
      context: .
      dockerfile: ai-bid-gateway/Dockerfile
    container_name: ai-bid-gateway
    ports:
      - "8090:8090"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
    depends_on:
      - ai-bid-knowledge
      - ai-bid-ai
    networks:
      - bid-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8090/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ai-bid-user:
    build:
      context: .
      dockerfile: ai-bid-user/Dockerfile
    container_name: ai-bid-user
    ports:
      - "8081:8081"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/ai_bid
      - SPRING_DATASOURCE_USERNAME=postgres
      - SPRING_DATASOURCE_PASSWORD=postgres
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - bid-network

  ai-bid-project:
    build:
      context: .
      dockerfile: ai-bid-project/Dockerfile
    container_name: ai-bid-project
    ports:
      - "8082:8082"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/ai_bid
      - SPRING_DATASOURCE_USERNAME=postgres
      - SPRING_DATASOURCE_PASSWORD=postgres
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - bid-network

  ai-bid-material:
    build:
      context: .
      dockerfile: ai-bid-material/Dockerfile
    container_name: ai-bid-material
    ports:
      - "8083:8083"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/ai_bid
      - SPRING_DATASOURCE_USERNAME=postgres
      - SPRING_DATASOURCE_PASSWORD=postgres
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - bid-network

  ai-bid-document:
    build:
      context: .
      dockerfile: ai-bid-document/Dockerfile
    container_name: ai-bid-document
    ports:
      - "8084:8084"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/ai_bid
      - SPRING_DATASOURCE_USERNAME=postgres
      - SPRING_DATASOURCE_PASSWORD=postgres
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - bid-network

  ai-bid-bid:
    build:
      context: .
      dockerfile: ai-bid-bid/Dockerfile
    container_name: ai-bid-bid
    ports:
      - "8085:8085"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/ai_bid
      - SPRING_DATASOURCE_USERNAME=postgres
      - SPRING_DATASOURCE_PASSWORD=postgres
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - bid-network

  ai-bid-frontend:
    build:
      context: ./ai-bid-frontend
      dockerfile: Dockerfile
    container_name: ai-bid-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8090
    depends_on:
      - ai-bid-gateway
    networks:
      - bid-network

volumes:
  postgres_data:
  redis_data:

networks:
  bid-network:
    driver: bridge
"@

[System.IO.File]::WriteAllText("C:\ai-bid\docker-compose.yml", $content, [System.Text.Encoding]::UTF8)
Write-Host "Done"
