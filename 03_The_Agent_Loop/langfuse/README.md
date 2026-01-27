# LangFuse Setup

This folder contains the LangFuse Docker Compose configuration for local tracing.

## Quick Start

Run LangFuse locally:

```bash
docker compose up -d
```

This will start all services including the web interface at http://localhost:3000

## Configuration

The `.env` file contains the initialization settings for LangFuse. When the server starts for the first time, it will automatically:

1. Create an organization named "AIE9"
2. Create a project named "Agent Loop"
3. Create an admin user with the credentials you provided
4. Set up API keys with:
   - **Public Key**: `pk-lf-aie9-dev`
   - **Secret Key**: `sk-lf-aie9-dev-secret`

## Using with The_Agent_Loop_Assignment.py

When running the assignment, use these keys:

```
LangFuse Public Key: pk-lf-aie9-dev
LangFuse Secret Key: sk-lf-aie9-dev-secret
LangFuse Base URL: http://localhost:3000
```

## Services

- **Web UI**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **ClickHouse**: localhost:8123, localhost:9000
- **MinIO**: localhost:9090
- **Redis**: localhost:6379

## Stopping

```bash
docker compose down
```

To remove all data volumes:

```bash
docker compose down -v
```