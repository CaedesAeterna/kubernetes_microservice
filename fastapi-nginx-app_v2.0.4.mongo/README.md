# FastAPI + Nginx Example (two containers)

This small project runs a minimal FastAPI app behind an Nginx reverse proxy using Docker Compose.

Files added:
- `app/` - FastAPI application and Dockerfile
- `nginx/default.conf` - Nginx config to proxy to FastAPI
- `docker-compose.yml` - service definitions

Quick start:

1. Build and start containers:

```bash
docker compose up --build
```

2. Open http://localhost in your browser. The request will be proxied to the FastAPI app on port 8000.

3. Health endpoint: http://localhost/healthz

Notes:
- The FastAPI container listens on port 8000 internally; Nginx proxies requests from port 80.
- Adjust `nginx/default.conf` if you need additional headers or TLS.
