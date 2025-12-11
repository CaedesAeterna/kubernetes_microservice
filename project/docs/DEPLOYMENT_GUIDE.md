# Media Tracker App - Deployment & Usage Guide

## 1. Prerequisites
*   **Minikube** installed and running (`minikube start`).
*   **Ingress Addon** enabled:
    ```bash
    minikube addons enable ingress
    ```
*   **Docker** (client) installed.

## 2. Project Structure
The project is organized as follows:
*   `services/`: Source code for microservices.
*   `k8s/`: Kubernetes manifests (Apps & Infra).
*   `scripts/`: Automation scripts (`deploy.sh`, `deploy_next.sh`).
*   `docs/`: Documentation.
*   `VERSION`: Semantic version tracker.

## 3. How to Deploy

### Option A: Fresh Deployment (Reset everything)
Use this script to create namespaces, deploy infrastructure (Kafka, DBs, Redis), build initial images, and deploy apps.
```bash
./scripts/deploy.sh
```

### Option B: Update Code (Rolling Update)
If you made changes to the code (`services/`), use this script. It will:
1.  Increment the version number (e.g., `1.1.10` -> `1.1.11`).
    *   *Note: Bumps Minor version if Patch > 99.*
2.  Build new Docker images with the new tag.
3.  Update Kubernetes deployments to roll out the new version.
```bash
./scripts/deploy_next.sh
```

## 4. Accessing the Application

**Base URL:** `http://<minikube-ip>` (Port 80 via Ingress)
*If using Minikube on Linux/Docker driver, Ingress might be exposed on a NodePort. Check `./scripts/deploy.sh` output.*

**Standard URLs:**
*   **Login/Register:** `http://<ip>/auth/login`
*   **Browse/Search Media:** `http://<ip>/media`
*   **My Library:** `http://<ip>/library`
*   **My Profile:** `http://<ip>/profile`
*   **Global History:** `http://<ip>/library/history`
*   **Dashboard:** `http://<ip>/dashboard`

### Common Minikube IP Check
```bash
minikube ip
# Example: 192.168.49.2
```
If Ingress is on NodePort (common on Linux without `minikube tunnel`):
```bash
minikube service ingress-nginx-controller -n default --url
# or check
minikube service ingress-nginx-controller -n ingress-nginx --url
```

## 5. Troubleshooting
*   **Login fails:** Ensure `user-service` is connected to Postgres.
*   **Media list empty:** Ensure `media-service` is connected to Mongo.
*   **Kafka errors:** Check `strimzi-cluster-operator` logs.
*   **Ingress 404/503:** Verify Ingress resource `kubectl get ingress -n app` and check pod logs.

## 6. Architecture Status
*   **User Service (v1.1.X):** Node.js + Postgres. Handles Auth, Library (with Season/Episode tracking), Profile Stats, History, JSON API.
*   **Media Service (v1.1.X):** Python + MongoDB + Redis. Handles Media Catalog (with nested Seasons/Episodes), Search, Caching, JSON API.
*   **Notification Service (v1.1.X):** Python + FastAPI (Consumer). Listens to `user-registered` events for email simulation (Pub/Sub Pattern).
*   **Dashboard Service (v1.1.X):** Python + httpx. Aggregates data from other services, implements Circuit Breaker.
*   **Messaging:** Kafka (Strimzi) - configured for Fan-out (Pub/Sub).
*   **Persistent Storage:** PostgreSQL, MongoDB (Replica Set), Redis (for Caching).