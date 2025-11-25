# Sagarr Implementation Plan

This document outlines the step-by-step plan to build Sagarr, an AI-powered media recommendation engine.

## Phase 1: Foundation & Infrastructure
*Goal: Set up the project structure, backend API skeleton, frontend skeleton, and authentication.*

- [x] **Task 1.1: Project Initialization**
    - Create a monorepo structure (`/backend`, `/frontend`).
    - Initialize Git repository.
    - Create a basic `README.md` and `.gitignore`.
    - **Dependencies:** None

- [x] **Task 1.2: Backend Setup (FastAPI)**
    - Initialize a Python FastAPI project in `/backend`.
    - Configure `poetry` or `requirements.txt` for dependency management.
    - Create a basic "Hello World" endpoint (`GET /api/health`).
    - Configure CORS to allow requests from the frontend.
    - **Dependencies:** 1.1

- [x] **Task 1.3: Frontend Setup (React + Vite)**
    - Initialize a React project using Vite in `/frontend`.
    - Install necessary libraries: `axios` (or `fetch` wrapper), `react-router-dom`, `tanstack-query` (optional but recommended), and a UI component library (e.g., `shadcn/ui` or `Mantine`).
    - Create a basic layout with a placeholder Dashboard page.
    - **Dependencies:** 1.1

- [x] **Task 1.4: Database Configuration (SQLite)**
    - Set up SQLite database connection in FastAPI (using `SQLAlchemy` or `Tortoise-ORM`).
    - Define the initial `User` model (id, plex_id, username, email, role).
    - Create a migration script or initialization function to create tables on startup.
    - **Dependencies:** 1.2

- [x] **Task 1.5: Plex OAuth Implementation**
    - Register the application concept (Plex doesn't require strict app registration like Google, but we need the flow).
    - **Backend:** Create endpoints for:
        - `GET /api/auth/login`: Redirects user to Plex sign-in.
        - `GET /api/auth/callback`: Handles the callback, exchanges code for token, fetches user info from Plex API (`https://plex.tv/api/v2/user`).
        - `POST /api/auth/logout`: Clears session.
    - **Frontend:** Create a Login page with a "Sign in with Plex" button.
    - **Logic:** On successful login, check if user exists in DB; if not, create them. Issue a JWT session cookie.
    - **Dependencies:** 1.2, 1.3, 1.4

## Phase 2: Core Integrations (Data Ingestion)
*Goal: Connect to Tautulli for history and Overseerr for availability.*

- [x] **Task 2.1: Tautulli Connector**
    - Create a service module `services/tautulli.py`.
    - Implement function `get_user_history(user_id, limit=100)`: Fetches watch history from Tautulli API.
    - Implement function `get_users()`: Fetches list of users to map Plex IDs to Tautulli IDs.
    - **Config:** Add `TAUTULLI_URL` and `TAUTULLI_API_KEY` to environment variables/settings.
    - **Dependencies:** 1.2

- [x] **Task 2.2: User Mapping Logic**
    - Update the Login flow (Task 1.5) to trigger a "Sync User" background task.
    - **Logic:** When a user logs in, search Tautulli users for a matching email or username. Store the `tautulli_user_id` in the `User` table.
    - **Dependencies:** 1.5, 2.1

- [x] **Task 2.3: Overseerr Connector**
    - Create a service module `services/overseerr.py`.
    - Implement function `check_availability(tmdb_id)`: Checks if an item is available or requested.
    - Implement function `request_media(tmdb_id, media_type)`: Sends a request to Overseerr.
    - **Config:** Add `OVERSEERR_URL` and `OVERSEERR_API_KEY` to environment variables.
    - **Dependencies:** 1.2

- [x] **Task 2.3b: Smart Series Requesting**
    - Update `services/overseerr.py` to handle TV requests differently.
    - **Logic:** When requesting a TV show, explicitly request Seasons 1, 2, and 3 (if available) instead of just the default behavior.
    - **Dependencies:** 2.3



- [x] **Task 2.4: Database Schema Expansion**
    - Add models for:
        - `RecommendationCache`: Stores generated recommendations for a user (user_id, json_blob, created_at).
        - `UserPreference`: Stores "Seen It" / Thumbs Up/Down status (user_id, tmdb_id, rating, timestamp).
    - **Dependencies:** 1.4

## Phase 3: The "Brain" (AI & Scheduling)
*Goal: Implement the AI recommendation logic and the background scheduler.*

- [x] **Task 3.1: AI Service Interface**
    - Create an abstract base class `AIProvider`.
    - Implement concrete classes for:
        - `OpenAIProvider` (GPT-4o, etc.)
        - `GenericProvider` (for Ollama/LocalAI compatible endpoints).
    - **Config:** Add `AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL` settings.
    - **Dependencies:** 1.2

- [x] **Task 3.2: Prompt Engineering & Logic**
    - Design the prompt to accept: "User's Top 10 Movies", "User's Recent Watches", "User's Dislikes".
    - **Output Format:** JSON structure with `categories` (list of objects: `title`, `reason`, `items` [list of tmdb_ids]).
    - Implement `generate_recommendations(user_id)` function that orchestrates fetching history -> calling AI -> parsing JSON.
    - **Dependencies:** 2.1, 3.1

- [x] **Task 3.3: Metadata Enrichment**
    - The AI gives TMDb IDs. We need posters/titles.
    - Implement a `MetadataService` (using TMDb API or Overseerr proxy) to fetch details for the recommended IDs.
    - **Dependencies:** 3.2

- [x] **Task 3.4: Background Scheduler**
    - Set up a scheduler (e.g., `APScheduler` or a simple background loop).
    - Create a job `refresh_recommendations` that runs nightly (or on demand) for all active users.
    - Store results in `RecommendationCache`.
    - **Dependencies:** 2.4, 3.2, 3.3

## Phase 4: UI Implementation
*Goal: Build the user-facing dashboard and interaction flows.*

- [x] **Task 4.1: Dashboard UI**
    - Create a `RecommendationRow` component (horizontal scroll).
    - Create a `MediaCard` component (Poster, Title).
    - Fetch cached recommendations from `GET /api/recommendations` and render them.
    - **Dependencies:** 1.3, 3.4

- [x] **Task 4.7: Split Recommendations (Movies vs TV)**
    - Update Backend to generate and store separate lists for Movies and TV.
    - Update Frontend Dashboard to include a toggle/tab system.
    - **Dependencies:** 4.1

- [x] **Task 4.2: Media Card Actions**
    - Implement hover/click state on `MediaCard`.
    - **Logic:**
        - Call backend `GET /api/media/{tmdb_id}/status` (proxies Overseerr).
        - Show "Request" or "Watchlist" button based on status.
        - Implement click handlers to trigger backend actions.
    - **Dependencies:** 2.3, 4.1

- [x] **Task 4.3: "Seen It" Workflow**
    - Add an "Eye" icon to the Media Card.
    - Create a Modal/Popover that asks: "Did you like it?" (Thumbs Up / Down).
    - **Backend:** `POST /api/media/{tmdb_id}/rate` -> Updates `UserPreference` table.
    - **Frontend:** Optimistically hide the card from the UI upon submission.
    - **Dependencies:** 2.4, 4.2

- [x] **Task 4.4: Comprehensive Action Logging**
    - Update `POST /api/media/{tmdb_id}/request` to also insert a `UserPreference` record (Rating: 2) upon success.
    - Ensure "Skip" actions are logged as dislikes (Rating: -1).
    - **Dependencies:** 4.2

- [x] **Task 4.5: User History & Data Management UI**
    - Create a "My History" page accessible from the User Profile.
    - Display a paginated list of all `UserPreference` records (Requests, Likes, Dislikes).
    - **Actions:**
        - **Change Rating:** Allow toggling between Thumbs Up/Down.
        - **Delete:** Allow removing a record entirely (undoing the interaction).
    - **Backend:** Update `POST /api/media/{tmdb_id}/rate` to handle updates, and add `DELETE /api/media/{tmdb_id}/rate`.
    - **Dependencies:** 4.4

- [x] **Task 4.6: Dashboard Cleanup**
    - Remove the raw "Backend Status" JSON dump from the main Dashboard view.
    - Ensure the dashboard looks clean and consumer-ready.
    - **Dependencies:** 4.1

- [x] **Task 4.8: Documentary Support**
    - **Backend:** Update `services/recommendations.py` to identify documentaries (via Genre ID 99) and separate them into a third list.
    - **Frontend:** Add a "Documentaries" tab to the Dashboard.
    - **Dependencies:** 4.7

## Phase 5: Polish & Deployment
*Goal: Make it production-ready.*

- [x] **Task 5.1: Admin Settings Page**
    - Create a frontend page for Admins only.
    - Allow configuration of API Keys (Tautulli, Overseerr, AI, TMDb) and Model selection via UI, including an optional fallback AI provider/model to minimize cost by preferring cheaper/free options first.
    - Add backend "config check" endpoints:
        - `GET /api/admin/test/tautulli` -> verifies URL/API key reachability and basic auth.
        - `GET /api/admin/test/overseerr` -> verifies URL/API key and a simple availability call.
        - `GET /api/admin/test/ai` -> runs a tiny prompt against the configured AI provider.
        - `GET /api/admin/test/tmdb` -> verifies TMDb API key by fetching a known movie.
    - Wire a "Test" button under each configurable integration (Tautulli, Overseerr, AI, TMDb) in the Admin UI that calls the corresponding backend test endpoint and surfaces success/failure inline.
    - Add per-section "Save" buttons for Tautulli, Overseerr, AI, and TMDb so each integration can be saved independently alongside its test control.
    - **Dependencies:** 1.3, 1.4

- [x] **Task 5.2: Dockerization**
    - Create `Dockerfile` for Backend.
    - Create `Dockerfile` for Frontend (multi-stage build: build React -> serve with Nginx or serve static via FastAPI).
    - Create `docker-compose.yml` orchestrating the service + volume for SQLite DB.
    - **Dependencies:** 1.1, 1.2, 1.3

- [x] **Task 5.3: Testing & Documentation**
    - Run end-to-end manual tests.
    - Write `docs/setup.md` for users.
    - Finalize `README.md`.
    - **Dependencies:** All previous tasks.

## Phase 6: Saltbox Integration (Ready for Deployment)
*Goal: Make Sagarr deployable on a standard Saltbox stack with Traefik, proper permissions, and standard paths.*

- [x] **Task 6.1: Docker Compose for Saltbox**
    - Update `docker-compose.yml`:
        - Add `networks: proxy: external: true`.
        - Add `restart: unless-stopped` to services.
        - Add `user: "${PUID}:${PGID}"` support (or ensure internal permissions work with mapped volumes).
        - Add Traefik labels to the **Frontend** service:
            - `traefik.enable=true`
            - `traefik.http.routers.sagarr.rule=Host(\`sagarr.YOURDOMAIN.COM\`)` (using env var for domain).
            - `traefik.http.routers.sagarr.entrypoints=websecure`
            - `traefik.http.routers.sagarr.tls.certresolver=letsencrypt` (or standard resolver).
            - `traefik.http.services.sagarr.loadbalancer.server.port=80` (internal nginx port).
    - **Dependencies:** 5.2

- [x] **Task 6.2: Environment Standardization**
    - Create `saltbox.env.example` containing:
        - `PUID`, `PGID`, `TZ`.
        - `DOMAINNAME` (for Traefik rules).
        - `SAGARR_HOST` (for internal referencing).
        - All app secrets (`SECRET_KEY`, `TMDB_API_KEY`, etc.).
    - Update `backend/app/config.py` to respect `TZ` if needed (mostly for logging timestamps).
    - **Dependencies:** 5.2

- [x] **Task 6.3: Path & Permission Hardening**
    - Ensure `Dockerfile` setups respect user permissions for the `/app/data` volume (SQLite DB).
    - Verify that the application writes logs/DB to the mounted volume correctly when running as a non-root user (Saltbox standard).
    - **Dependencies:** 5.2

- [x] **Task 6.4: Admin Bootstrap & Persistence**
    - *Completed in Phase 5 polish.*
    - (First user becomes admin; settings persist to DB).

- [x] **Task 6.5: Saltbox Documentation**
    - Create `docs/saltbox_setup.md`.
    - Instructions for:
        1. Creating the folder structure (`/opt/sagarr`).
        2. Copying `docker-compose.yml` and `.env`.
        3. Setting up the proxy network if missing.
        4. Running `docker compose up -d`.
    - **Dependencies:** 6.1, 6.2
