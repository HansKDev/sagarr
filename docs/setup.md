# Sagarr Setup Guide

This guide will help you set up and run Sagarr, the AI-powered media recommendation engine.

## Prerequisites

- **Docker** and **Docker Compose** installed on your system.
- A **Plex** account.
- **Tautulli** (running and accessible).
- **Overseerr** (running and accessible).
- An **OpenAI API Key** (or a compatible local AI endpoint like Ollama).

## Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/sagarr.git
    cd sagarr
    ```

2.  **Configuration**
    Create a `.env` file in the `backend` directory (or rely on the Admin UI later).
    
    Example `backend/.env` (for local dev using Vite on 5173; when using Docker, this is overridden by `FRONTEND_URL` in `docker-compose.yml`):
    ```ini
    # Security
    SECRET_KEY=your_super_secret_key_here
    
    # URLs (for Docker, use the externally reachable frontend URL)
    FRONTEND_URL=http://localhost:8081
    
    # Optional Pre-configuration (can also be set in UI)
    TAUTULLI_URL=http://192.168.1.100:8181
    TAUTULLI_API_KEY=your_tautulli_key
    OVERSEERR_URL=http://192.168.1.100:5055
    OVERSEERR_API_KEY=your_overseerr_key
    AI_PROVIDER=openai
    AI_API_KEY=sk-your-openai-key
    AI_MODEL=gpt-4o
    ```

3.  **Run with Docker Compose**
    ```bash
    docker-compose up -d --build
    ```

4.  **Access the Application**
    Open your browser and navigate to `http://localhost:8081`.

## First Run

1.  **Login**: Click "Sign in with Plex". You will be redirected to Plex to authenticate.
2.  **Admin Settings**: Once logged in, click the "Admin" link in the navigation bar.
3.  **Configure Services**: Ensure Tautulli, Overseerr, and AI settings are correct. Click "Save Settings".
4.  **Wait for Sync**: The system will sync your watch history from Tautulli (this happens in the background).
5.  **Enjoy**: Recommendations will appear on your Dashboard once the nightly job runs or is triggered manually.

## Troubleshooting

-   **Backend Logs**: `docker logs sagarr-backend`
-   **Frontend Logs**: `docker logs sagarr-frontend`
-   **Database**: The SQLite database is stored in the `sagarr-data` volume.

## Development

To run locally without Docker:

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
