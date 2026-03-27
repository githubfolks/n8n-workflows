# Social Media Automation Backend (FastAPI)

Production-ready backend for automating content generation and social media publishing.

## Features
- **Clean Architecture**: Modular structure (API, Core, Services, Models).
- **FastAPI**: High performance async API.
- **PostgreSQL**: Robust data persistence.
- **MinIO**: S3-compatible object storage for media assets.
- **Ollama Integration**: Local AI text generation support.
- **Scheduler**: Background tasks using APScheduler.
- **Dockerized**: Easy deployment with Docker Compose.

## Setup

1.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in your credentials.
    ```bash
    cp .env.example .env
    ```

2.  **Run with Docker**:
    The easiest way to run the full stack (App + DB + MinIO).
    ```bash
    docker-compose up --build
    ```

3.  **Access**:
    -   **API**: http://localhost:8000
    -   **Docs**: http://localhost:8000/docs
    -   **MinIO Console**: http://localhost:9001 (User/Pass: minioadmin)
    -   **Image Service API**: http://localhost:8001/docs
    -   **Video Service API**: http://localhost:8002/docs

## Image Generation Service

A standalone microservice for Stable Diffusion image generation.

-   **Endpoint**: `POST /generate`
-   **Config**: Controlled by `SD_API_URL`.

## Video Generation Service

A standalone microservice for creating 9:16 videos using FFmpeg.

-   **Endpoint**: `POST /generate`
-   **Features**: Concatenates images, adds audio, and uploads to MinIO.

## Local Development

If you want to run locally without Docker for the app:

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Start Dependencies**:
    Ensure Postgres and MinIO are running (e.g., via docker-compose).
3.  **Run App**:
    ```bash
    uvicorn app.main:app --reload
    ```

## API Endpoints

-   `POST /api/v1/auth/signup`: Register a new user.
-   `POST /api/v1/auth/login/access-token`: Get JWT token.
-   `POST /api/v1/content/`: Generate content (Ollama/OpenAI).
-   `POST /api/v1/posts/`: Schedule a post.

## Architecture

-   `app/core`: Configuration, Security, DB session.
-   `app/api`: Routes and Dependencies.
-   `app/services`: Business logic (Auth, Content, Media, Social).
-   `app/models`: Database tables (SQLModel).
