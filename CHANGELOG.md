# Changelog

All notable changes to Sagarr will be documented in this file.

This project follows a simple, semantic-style versioning scheme: `MAJOR.MINOR.PATCH`.

## [0.1.0] - 2025-11-25

### Added
- Plex PIN-based authentication flow, including login and callback endpoints.
- User persistence in SQLite with Plex IDs, basic profile data, and `is_admin` flag.
- Admin bootstrap: first successful Plex user becomes admin.
- Admin-only settings API and UI covering:
  - Tautulli URL/API key (with connectivity test).
  - Overseerr URL/API key (with connectivity test).
  - AI provider/API key/model (with connectivity test).
  - Optional AI fallback provider/API key/model.
  - TMDb API key (with connectivity test).
- Persistent configuration store:
  - `app_settings` table for integration keys and URLs.
  - Startup loader that applies DB-stored settings over environment defaults.
- Tautulli integration:
  - User and history fetch with support for multiple API response shapes.
  - Live settings usage and support for bare `host:port` URLs (e.g. `tautulli:8181`).
- Overseerr integration:
  - Availability check and media request APIs using live settings.
  - Support for bare `host:port` URLs (e.g. `overseerr:5055`).
- AI provider abstraction with:
  - Native OpenAI, Anthropic Claude, and Google Gemini providers.
  - Generic OpenAI-compatible HTTP provider (Ollama, OpenRouter, Mistral, Groq, etc.).
  - Chained provider that falls back from primary to secondary when errors occur.
- Recommendation engine:
  - Uses Tautulli history (movies, TV, documentaries) plus explicit likes/dislikes.
  - Builds context slices (top/recent movies and TV, series titles, documentary samples).
  - Filters out explicit adult content using Tautulli metadata and TMDb `adult` flag.
  - Avoids recommending:
    - Titles already seen in Plex/Tautulli history.
    - Titles already rated/seen within Sagarr.
- TMDb-based metadata enrichment for titles, posters, and overviews.
- Media actions:
  - Overseerr-backed status and request endpoints.
  - Rating endpoint to store likes/dislikes and “seen it” signals.
- Frontend SPA:
  - Login, Dashboard, History, and Admin pages with protected routing.
  - Admin UI wired to the settings API and config test endpoints.
  - Dashboard tabs for Movies, TV Series, and Docs, with per-row separators.
  - Media cards with Request/Seen It/Skip actions and improved layout.
- Docker & deployment:
  - Backend and frontend Dockerfiles (FastAPI + Nginx/Vite).
  - `docker-compose.yml` with:
    - Backend bound to `/opt/sagarr/data:/app/data` for DB persistence.
    - Saltbox-friendly networking and Traefik labels.
- Documentation:
  - PRD (`docs/specs.md`), implementation plan (`docs/todo.md`).
  - Local setup guide (`docs/setup.md`) and Saltbox-specific guide (`docs/saltbox_setup.md`).
  - README disclaimer marking Sagarr as early beta / not production-hardened.

### Changed
- Admin UI visibility:
  - Only `is_admin` users see the Admin navigation link and can access `/admin`.
  - Non-admins are redirected away from admin routes and receive 403 from admin APIs.
- Recommendation serialization:
  - Extended cache payload to capture likes/dislikes, watched titles, rated TMDb IDs, and split lanes (`movies`, `tv`, `documentaries`).
- Frontend styling:
  - Applied Sagarr branding (logo, theme, buttons, and favicon).

### Fixed
- Multiple Tautulli and Overseerr issues:
  - Stale URL/API key caching inside service instances.
  - Admin tests incorrectly reporting 0 users or UNKNOWN status.
  - Docker networking mismatches on Saltbox by ensuring services share the `saltbox` network.
- Auth callback stability:
  - Resolved `httpx` client reuse bug that caused “client has been closed” errors.
  - Improved error messages for incomplete Plex PIN authorizations.
- Recommendation and metadata errors:
  - Properly register media/recommendation routers.
  - Gracefully handle JSON parsing errors and surface clear 400/500 responses.

