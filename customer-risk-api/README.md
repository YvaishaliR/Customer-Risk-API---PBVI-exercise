# Customer Risk API

Customer Risk API is a demo REST service that exposes synthetic customer risk-score data backed by a PostgreSQL database. It is intended as a training system for exploring API design, containerised deployment, and basic authentication patterns — all data is synthetic and no real customer information is used at any point.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Quickstart

```bash
cp .env.example .env
# Open .env and fill in POSTGRES_PASSWORD and API_KEY
docker compose up
```

The API will be available at `http://localhost:8000`.

## API Usage

All requests must include an `X-API-Key` header whose value matches the `API_KEY` set in your `.env` file.

```bash
curl -s http://localhost:8000/customers \
  -H "X-API-Key: your_api_key_here"
```

## Note

This is a training demo system. All customer records are synthetically generated and do not represent real individuals or organisations.
