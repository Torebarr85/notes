+++
title = "Studio in volo new job"
date = 2026-03-05
draft = false
tags = ["corsi"]
+++

---
title: "Docker Compose in Practice: A Real-World Microservices Setup"
date: 2026-03-05
tags: ["docker", "docker-compose", "devops", "microservices"]
---

When you first encounter Docker Compose in a real project, it's rarely a simple two-service setup. This tutorial walks through a production-grade multi-service architecture — a Node.js backend, a React frontend, a Python processor, MongoDB, and RabbitMQ — all wired together with Docker Compose.

We'll cover the core concepts using real configuration files, so by the end you'll understand not just *what* each directive does, but *why* it's there.

---

## The Architecture

The project is an expense management system with five services:

- **mongodb** — persistent storage
- **rabbitmq** — message broker between services
- **backend** — Node.js REST API
- **frontend** — React app served by nginx
- **processor** — Python consumer reading from RabbitMQ
- **lakepublisher** — batch job that exports approved expenses (runs on demand)

```
frontend (3330) → backend (3000) → mongodb (27017)
                                 ↕
                             rabbitmq (5672)
                                 ↕
                            processor
```

---

## The `docker-compose.yml` — Production Configuration

### Infrastructure Services

```yaml
services:
  mongodb:
    image: mongo:7
    container_name: expenses-mongodb
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - expenses-network
```

A few things worth noting here:

- `restart: unless-stopped` — the container restarts automatically after a crash or reboot, but not if you manually stop it. This is the right default for production services.
- `volumes: mongodb_data:/data/db` — data is stored in a **named volume**, not on the host filesystem. Named volumes are managed by Docker and survive container recreation.
- `networks: expenses-network` — all services share a custom bridge network. This is what allows them to reach each other **by container name** (e.g. `mongodb://mongodb:27017`).

RabbitMQ adds one important concept: a **healthcheck**.

```yaml
  rabbitmq:
    image: rabbitmq:3-management-alpine
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
```

The healthcheck runs a command inside the container at regular intervals. Compose uses this to know when RabbitMQ is *actually ready* — not just started.

---

### Application Services and `depends_on`

```yaml
  backend:
    build:
      context: ./packages/backend
      dockerfile: Dockerfile
      target: production
    depends_on:
      mongodb:
        condition: service_started
      rabbitmq:
        condition: service_healthy
```

`depends_on` controls **startup order**. Two conditions are available:

| Condition | Meaning |
|---|---|
| `service_started` | Container has started (default) |
| `service_healthy` | Container has passed its healthcheck |

The backend waits for RabbitMQ to be `service_healthy` before starting — because connecting to a broker that isn't ready yet would cause the backend to crash on startup.

The backend also uses **environment variables** to configure service URLs:

```yaml
    environment:
      - MONGO_URI=mongodb://mongodb:27017/expenses
      - RABBITMQ_URL=amqp://admin:admin123@rabbitmq
```

Notice that `mongodb` and `rabbitmq` here are not hostnames you configured manually — they are the **service names** from the Compose file. Docker's internal DNS resolves them automatically within the shared network.

---

### Volumes with `:Z` flag

```yaml
    volumes:
      - backend_uploads:/app/uploads:Z
```

The `:Z` flag is specific to **SELinux** systems (like Fedora/RHEL). It tells Docker to relabel the volume so the container has permission to read and write it. Without `:Z` on SELinux, you'd get silent permission denied errors.

---

### Profiles — On-Demand Services

```yaml
  lakepublisher:
    restart: "no"
    profiles:
      - batch
```

The `lakepublisher` is a batch job — it runs once to export data, then exits. Two things make it different:

- `restart: "no"` — don't restart after it finishes
- `profiles: [batch]` — it won't start with `docker compose up` by default

To run it explicitly:

```bash
docker compose --profile batch run lakepublisher
```

This pattern is useful for migrations, data exports, or any one-off task that shares the same network and environment as your main services.

---

## The `docker-compose.override.yml` — Development Configuration

Compose automatically merges `docker-compose.override.yml` on top of `docker-compose.yml` when you run `docker compose up`. This lets you keep production config clean while layering development-specific overrides.

```yaml
services:
  backend:
    build:
      context: ./packages/backend
      dockerfile: Dockerfile.dev
    environment:
      - NODE_ENV=development
    volumes:
      - ./packages/backend:/app
      - /app/node_modules
```

Key differences from production:

- Uses `Dockerfile.dev` instead of `Dockerfile` — typically runs the app with a file watcher (nodemon, ts-node-dev) instead of a compiled build
- Mounts the source code directly into the container: `./packages/backend:/app` — changes on your host are reflected immediately without rebuilding
- The `/app/node_modules` volume prevents the host's node_modules from overwriting the container's

The frontend override also changes the port:

```yaml
  frontend:
    ports:
      - "3030:3030"   # dev server port, not nginx
```

In production, the frontend is a static build served by nginx on port 80. In development, it's a live dev server (Vite/CRA) on port 3030.

---

## Common Commands

```bash
# Start all services (uses override automatically in dev)
docker compose up -d

# Start only production config (CI/CD, staging)
docker compose -f docker-compose.yml up -d

# Watch logs
docker compose logs -f backend

# Rebuild a specific service after code changes
docker compose up -d --build backend

# Run the batch job
docker compose --profile batch run lakepublisher

# Tear down (keep volumes)
docker compose down

# Tear down and delete all data
docker compose down -v
```

---

## Key Takeaways

- **Named volumes** persist data independently from containers
- **Custom networks** enable DNS-based service discovery by name
- **Healthchecks + depends_on** prevent startup race conditions
- **Override files** let you cleanly separate dev and prod config
- **Profiles** handle batch jobs and optional services without polluting your main stack
- **`:Z` flag** is required on SELinux systems for volume permissions

This pattern — infrastructure services with healthchecks, application services with proper dependencies, dev/prod split via override — is the foundation of most real-world Compose setups you'll encounter in a DevOps role.