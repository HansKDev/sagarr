# Product Requirements Document (PRD): Sagarr

## 1. Project Overview
**Sagarr** is a self-hosted, AI-powered media recommendation engine designed to fit seamlessly into the "Arr" stack (Sonarr, Radarr, Overseerr). It acts as a personalized discovery layer, bridging the gap between a user's past consumption (Plex/Tautulli) and future acquisition (Overseerr). By leveraging advanced LLMs, Sagarr generates dynamic, creative recommendation categories (e.g., "Gritty 80s Cyberpunk") tailored to each user's taste, rather than relying on static genres.

## 2. Core Requirements
*   **Personalized Discovery:** Recommendations must be based on the user's actual watch history from Tautulli.
*   **Seamless Integration:** Must integrate with Plex (Auth), Tautulli (History), and Overseerr (Availability/Requests) without manual data entry.
*   **Feedback Loop:** Must capture user sentiment ("Seen it", Thumbs Up/Down) to continuously refine the algorithm.
*   **Performance:** The UI must load recommendations instantly (sub-second) by utilizing background pre-calculation.
*   **Privacy:** All user preference data must be stored locally.

## 3. Core Features
*   **Dynamic AI Categories:** The system generates unique, descriptive category titles based on the user's specific mood and history.
*   **"Netflix-style" Dashboard:** A visual feed of recommendation rows, **separated into "Movies", "TV Series", and "Documentaries" tabs**.
*   **Smart Action Buttons:**
    *   *If Available:* "Add to Plex Watchlist".
    *   *If Missing:* "Request" (via Overseerr). **For TV Series, this defaults to requesting the first 3 seasons.**
*   **"Seen It" Workflow:** A mechanism for users to mark items as seen and immediately rate them (Thumbs Up/Down) to improve future suggestions.
*   **User Data Management:** A dedicated interface for users to view, edit, or delete their rating history (Requests, Likes, Dislikes) to have full control over their data.
*   **Hybrid AI Configuration:** Admins can configure different AI models for different tasks (e.g., cheap models for summarization, powerful models for creative generation).

## 4. Core Components
*   **Backend API (FastAPI):** Handles business logic, AI orchestration, and database interactions.
*   **Frontend UI (React):** A responsive Single Page Application (SPA) for users to browse and interact with recommendations.
*   **Scheduler:** A background worker that runs nightly to fetch Tautulli history and generate fresh recommendations.
*   **Database (SQLite):** Stores user mappings, preferences, and cached recommendations.
*   **Connectors:** Modules for communicating with Plex, Tautulli, Overseerr, and AI Providers.

## 5. App/User Flow
1.  **Login:** User logs in via **Plex OAuth**.
2.  **Mapping:** System identifies the user and links them to their **Tautulli** history (1-to-1 mapping).
3.  **Browse:** User sees a dashboard of pre-calculated, AI-generated recommendation rows.
4.  **Interact:**
    *   User clicks a movie card.
    *   System checks **Overseerr** for availability.
    *   *Scenario A (Missing):* User clicks "Request". Item is added to Overseerr, hidden from feed, and **logged as a high-priority positive preference** (Rating: 2).
    *   *Scenario B (Available):* User clicks "Watchlist". Item is added to Plex Watchlist.
    *   *Scenario C (Already Seen):* User clicks "Seen It" (eye icon) -> Selects "Thumbs Up" (Rating: 1) or "Down" (Rating: -1). Item is hidden and preference is saved.
    *   *Scenario D (Skip):* User clicks "Skip". Item is hidden and logged as a dislike (Rating: -1).
5.  **Refine:** Background job uses new feedback to adjust the next batch of recommendations.
6.  **History:** Users can view a log of their interactions (Requests, Likes, Dislikes) to manage their preferences.

## 6. Techstack
*   **Backend:** Python (FastAPI)
*   **Frontend:** React (Vite)
*   **Database:** SQLite
*   **AI Integration:** LangChain or direct API calls (OpenAI, Anthropic, Ollama)
*   **Containerization:** Docker & Docker Compose

## 7. Deployment Targets
*   **Self-hosted Docker:** Single-node Docker Compose deployment on a homelab or VPS.
*   **Saltbox-style Stack:** Optional integration into a Saltbox-like media stack, using a shared reverse proxy (e.g., Traefik) and consistent app/service naming.

## 8. Implementation Plan

### Phase 1: Foundation
*   Initialize Git repository and project structure (monorepo).
*   Set up FastAPI backend with SQLite connection.
*   Set up React frontend with basic routing.
*   Implement Plex OAuth flow.

### Phase 2: Data Ingestion & Integration
*   Implement Tautulli connector to fetch user history.
*   Implement Overseerr connector to check media availability.
*   Create database schemas for Users and Preferences.

### Phase 3: The "Brain" (AI)
*   Implement the Hybrid AI service.
*   Develop the prompt engineering strategy for dynamic categories.
*   Build the Scheduler for nightly recommendation generation.

### Phase 4: UI & Interaction
*   Build the Dashboard component.
*   Implement the Media Card with "Request/Watchlist" logic.
*   Implement the "Seen It" / Rating modal.

### Phase 5: Polish & Release
*   Dockerize the application.
*   Add admin settings page for AI configuration.
*   Perform end-to-end testing.
*   Write documentation and release.

### Phase 6: Saltbox Integration (Ready for Deployment)
*   **Container Standardization:**
    *   Support standard Saltbox environment variables: `PUID`, `PGID`, `TZ`.
    *   Ensure containers restart automatically (`restart: unless-stopped`).
*   **Reverse Proxy (Traefik):**
    *   Configure `docker-compose.yml` with Traefik labels for automatic SSL and domain routing (e.g., `sagarr.YOURDOMAIN.COM`).
    *   Connect services to the standard `proxy` Docker network.
*   **Configuration & Secrets:**
    *   Consolidate all configuration into a single `.env` file template compatible with Saltbox's `sb_install` patterns.
    *   Ensure paths (config, data) are mapped to standard locations (`/opt/sagarr/config`, etc.).
*   **Documentation:**
    *   Create a specific `docs/saltbox_setup.md` guide detailing the install process on a Saltbox server.
