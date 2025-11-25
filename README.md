# Sagarr

**Sagarr** is an AI-powered media recommendation engine designed to integrate seamlessly with the "Arr" stack (Sonarr, Radarr, Overseerr) and Plex/Tautulli. It acts as a personalized discovery layer, using your watch history to generate dynamic, creative recommendations.

> ⚠️ **Status: Early Beta / Not Production-Hardened**  
> Sagarr is experimental software. It has not undergone a formal security review and is not intended for multi-tenant or high-risk environments.  
> Use at your own risk, and only expose it to the internet behind a trusted reverse proxy, with strong secrets and access limited to users you trust.

## Features

-   **AI-Powered Recommendations**: Uses LLMs (OpenAI, Ollama, etc.) to invent creative categories (e.g., "Gritty 80s Cyberpunk") based on your taste.
-   **Plex Integration**: Sign in with your Plex account.
-   **Tautulli Sync**: Automatically ingests your watch history to understand your preferences.
-   **Overseerr Integration**: Checks availability of recommendations and allows one-click requests.
-   **"Seen It" Tracking**: Mark items as seen and rate them to refine future suggestions.
-   **Modern UI**: A responsive, dark-mode interface built with React and Vite.

## Getting Started

See [docs/setup.md](docs/setup.md) for detailed installation instructions using Docker.

## Tech Stack

-   **Backend**: Python (FastAPI), SQLAlchemy, SQLite
-   **Frontend**: React, Vite
-   **AI**: OpenAI API / Generic OpenAI-compatible endpoints
-   **Containerization**: Docker, Docker Compose

## Documentation

-   [Product Requirements (PRD)](docs/specs.md)
-   [Implementation Plan](docs/todo.md)
-   [Setup Guide](docs/setup.md)

## License

MIT
