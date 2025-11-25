# Sagarr Saltbox Setup Guide

This guide explains how to deploy Sagarr on a [Saltbox](https://docs.saltbox.dev/) server or a similar Docker-based media stack.

## Prerequisites

*   A working Saltbox installation (or Docker + Traefik setup).
*   A configured `proxy` Docker network (standard in Saltbox).
*   A domain name configured in Traefik (e.g., `sagarr.yourdomain.com`).

## Installation Steps

1.  **Create the Application Directory**
    SSH into your server and create the directory structure:
    ```bash
    mkdir -p /opt/sagarr
    cd /opt/sagarr
    ```

2.  **Clone or Copy Files**
    You can clone the repository or simply copy the `docker-compose.yml` and `saltbox.env.example` files.
    ```bash
    git clone https://github.com/yourusername/sagarr.git .
    # OR copy files manually
    ```

3.  **Configure Environment**
    Copy the example environment file and edit it:
    ```bash
    cp saltbox.env.example .env
    nano .env
    ```
    *   **DOMAINNAME**: Set to your root domain (e.g., `myserver.com`).
    *   **FRONTEND_URL**: Set to `https://sagarr.myserver.com`.
    *   **SECRET_KEY**: Generate a random string.
    *   **PUID/PGID**: Set to your user ID (usually 1000).
    *   **Integrations**: You can set API keys here or later in the Admin UI.

4.  **Start the Application**
    ```bash
    docker compose up -d --build
    ```

5.  **Verify Deployment**
    *   Check logs: `docker compose logs -f`
    *   Access the web UI: `https://sagarr.yourdomain.com`
    *   **First Login**: The first user to log in via Plex will automatically become the **Admin**.

## Troubleshooting

*   **502 Bad Gateway**: Ensure the `sagarr-frontend` container is running and connected to the `proxy` network.
*   **Permission Errors**: Ensure `/opt/sagarr` is owned by your user (`chown -R $USER:$USER /opt/sagarr`).
*   **Database Locked**: Ensure no other process is accessing `sagarr.db`.

## Updates

To update Sagarr:
```bash
cd /opt/sagarr
git pull
docker compose up -d --build
```
