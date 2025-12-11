# Technology Stack

## Infrastructure & Orchestration
*   **Cloud Provider:** DigitalOcean
*   **Orchestration:** Kubernetes (K8s)
*   **API Gateway / Ingress Controller:** NGINX

## Databases
*   **Relational:** PostgreSQL (User data, Auth, structured relationships)
*   **NoSQL:** MongoDB (Media metadata, catalog, flexible schema documents)

## Message Broker
*   **Event Streaming:** Apache Kafka (Asynchronous communication between services)

## Backend Services
*   **Service A (e.g., Media/Search):** Python with **FastAPI**
*   **Service B (e.g., User/Tracker):** Node.js with **Express**
*   **Service C (Notification):** Python with **FastAPI** (Event-Driven)

## Frontend & Templating
*   **Python Services:** **Jinja2** (Server-Side Rendering)
*   **Node.js Services:** **EJS** (Embedded JavaScript templating)
