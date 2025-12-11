# Product Requirements Document (PRD) - Media Tracker App

## 1. Introduction
The Media Tracker App is a microservices-based application designed to help users track their consumption of various forms of media, including series, movies, web novels, novels, and physical books. It allows users to manage their libraries, track progress, and organize content.

## 2. Architecture
The application will follow a **microservice architecture** deployed on **Kubernetes**.

### Core Services:
*   **User Service:** Handles authentication (Auth0/OAuth2), user profiles, and preferences.
*   **Media Service:** Manages metadata for all media types (Movies, TV Series, Books, Novels).
*   **Tracker Service:** Records user progress (watched episodes, read chapters/pages).
*   **Search Service:** specialized indexing for fast retrieval of media items.
*   **Frontend (Web/Mobile):** The user interface.

## 3. Functional Requirements

### 3.1. Media Types Supported
The system must support the following media types:
*   **Series (TV/Anime):** Track by seasons and episodes.
*   **Movies:** Track watched status, rating, and review.
*   **Web Novels:** Track by chapter count.
*   **Novels (Light Novels/E-books):** Track by volume and chapter.
*   **Books (Physical/General):** Granular tracking options.

### 3.2. Detailed Tracking for Books
For the "Book" category, users must be able to track progress using multiple metrics:
*   **Page Number:** Current page read vs. total pages.
*   **Chapter:** Current chapter number or title.
*   **Chapter Section:** For granular tracking within long chapters or study textbooks.

### 3.3. User Library Management
*   **Status:** Users can mark items as *Plan to Watch/Read*, *Watching/Reading*, *Completed*, *On Hold*, or *Dropped*.
*   **Rating & Reviews:** Users can rate (1-10 or 5 stars) and review items.
*   **Favorites:** Mark specific items as favorites.

### 3.4. Search & Discovery
*   Search for media by title, author/director, genre, or tags.
*   Filter by media type and status.

## 4. Technical Stack (Proposed)
*   **Container Orchestration:** Kubernetes (DigitalOcean K8s).
*   **API Gateway / Ingress:** NGINX.
*   **Databases:** PostgreSQL (for relational data like users/auth) and MongoDB (for flexible media metadata).
*   **Message Broker:** Kafka.
*   **Backend:**
    *   Python (FastAPI).
    *   Node.js (Express).
*   **Frontend:** Server-Side Rendering (SSR) using:
    *   **Jinja2** (for Python/FastAPI services).
    *   **EJS** (for Node.js/Express services).

## 5. Deployment Strategy
*   CI/CD pipelines for automated testing and deployment.
*   Helm charts for managing Kubernetes manifests.
*   Secrets management via Kubernetes Secrets or external Vault.
