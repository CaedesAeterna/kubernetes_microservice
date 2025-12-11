# Project Structure

This document explains the organization of the codebase.

## Root Directory
*   `VERSION`: Text file containing the current semantic version (e.g., `1.1.2`). Used by deployment scripts.

## /services
Contains the source code for the microservices.
*   **user-service/**: Node.js/Express application.
    *   `index.js`: Entry point (with debug logging).
    *   `routes/`: 
        *   `auth.js`: Login/Register/Logout.
        *   `library.js`: Library management.
        *   `profile.js`: Stats calculation and dashboard.
    *   `models/`: Database interaction (`user.js`, `library.js`).
    *   `views/`: Bootstrap EJS templates.
    *   `config/`: Configuration (DB, Kafka).
    *   `migrate_v2.js`: Database migration script (adds season/episode columns).
*   **media-service/**: Python/FastAPI application.
    *   `app/main.py`: Entry point.
    *   `app/routers/`: `media.py` (CRUD + Search).
    *   `app/models.py`: Pydantic models.
    *   `app/database.py`: MongoDB connection.
    *   `app/templates/`: Bootstrap Jinja2 templates.
*   **notification-service/**: Python/FastAPI application.
    *   `app/main.py`: Entry point.
    *   `app/kafka_consumer.py`: Consumer for `user-registered` events (simulates email).
    *   `Dockerfile`: Container definition.

## /k8s
Contains Kubernetes YAML manifests.
*   **apps/**: Application-specific manifests.
    *   `user-service.yaml`: Deployment & Service for User Service.
    *   `media-service.yaml`: Deployment & Service for Media Service.
    *   `notification-service.yaml`: Deployment & Service for Notification Service.
*   **infra/**: Infrastructure components.
    *   `kafka-cluster.yaml`: Strimzi Kafka Cluster.
    *   `mongodb-replica-set.yaml`: MongoDB StatefulSet.
    *   `postgresql.yaml`: PostgreSQL StatefulSet.
    *   `ingress.yaml`: NGINX Ingress rules.
    *   `strimzi-rbac.yaml`: Role bindings.

## /scripts
Automation scripts for development and deployment.
*   `deploy.sh`: **Full Setup.** Deploys namespaces, infra, and apps from scratch.
*   `deploy_next.sh`: **Update.** Bumps version (smart increment), builds new images, and updates running deployments.

## /docs
Documentation files.
*   `PRD.md`: Product Requirements Document.
*   `IMPLEMENTATION_PLAN.md`: Implementation log and status.
*   `DEPLOYMENT_GUIDE.md`: Instructions on how to run/deploy.
*   `PROJECT_STRUCTURE.md`: This file.