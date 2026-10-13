# Deploying ChoreSpec on Synology NAS (or any Docker system)

This guide explains how to deploy the Family Chore App using Docker images hosted on GitHub Container Registry (GHCR).

## Prerequisites
- A Synology NAS with "Container Manager" (Docker) installed.
- SSH access to your NAS (needed to generate keys and read the initial PIN).
- If the GitHub repository is **Private**, you need a GitHub Personal Access Token (PAT) with `read:packages` scope.

> **Upgrading an existing installation?** The app now needs a `.env` file next to
> `docker-compose.yml`. Follow [Upgrading an existing installation](#upgrading-an-existing-installation)
> before pulling new images, or Postgres will not start.

## Fresh Installation

### 1. Prepare Folder
Create a folder on your NAS (e.g., `/volume1/docker/chorespec`) and upload two files into it:
- `docker-compose.yml`
- `.env.example`, renamed to `.env`

### 2. Configure `.env`
Open `.env` in a text editor and set:

1. **`POSTGRES_PASSWORD`**: a strong random password. You can generate one on the NAS with:
   ```bash
   openssl rand -hex 24
   ```
2. **`JWT_SECRET_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_PUBLIC_KEY`**: generate all three at once:
   ```bash
   sudo docker run --rm ghcr.io/frankandreas/family-chore-backend:latest python -m backend.generate_keys
   ```
   Paste the three printed lines into `.env`, replacing the empty entries.
3. **`VAPID_CLAIMS_EMAIL`**: your email address, as `mailto:you@example.com`.

Leave `COOKIE_SECURE=false` unless you serve the app over HTTPS (e.g. through a reverse proxy
with a certificate). With `true` on plain `http://`, nobody can log in.

> **Why the keys matter:** if they are left empty, the backend generates them inside the container.
> They are then replaced every time the container is recreated, which happens on every update.
> Everyone gets logged out and push notifications stop working.

Keep `.env` private: it contains your database password and signing keys.

### 3. Run the Application
Navigate to the folder and start the services:

```bash
cd /volume1/docker/chorespec  # Adjust path as needed
sudo docker-compose pull      # Downloads the latest images
sudo docker-compose up -d     # Starts the containers in background
```

*Alternatively, using Synology Container Manager UI:*
- Create a "**Project**".
- Helper: "Create project with existing docker-compose.yml".
- Select the folder (it must contain both `docker-compose.yml` and `.env`).
- Click "Next" -> "Done".

### 4. Access the App
Open your browser and navigate to:
`http://<YOUR_NAS_IP>:8080`

### 5. First Login
The system automatically seeds a default Admin user on first startup with a
**randomly generated PIN**, which is printed once in the backend log:

```bash
sudo docker logs chorespec-backend 2>&1 | grep "INITIAL PIN"
```

- **Username (Nickname)**: `Admin`
- **PIN**: the value from that log line. Change it after your first login.

If you lose the PIN on a fresh install, run `sudo docker-compose down -v` and start again to generate a new one. **This deletes all app data**, so only do it before the family starts using the app.

**Note:** The database persists in the `postgres_data` Docker volume; uploads and backups live in `chores_uploads` and `chores_backups`.

---

## Upgrading an Existing Installation

Older versions of `docker-compose.yml` (March to May 2026) had the database credentials built in:
user `chorespec_admin`, password `chorespec_password`. Your existing database was created with them.
Postgres only reads `POSTGRES_USER` / `POSTGRES_PASSWORD` when it creates a **new** database,
so changing them in `.env` does **not** change the password of an existing one.

1. **Back up first** (optional but recommended):
   ```bash
   sudo docker exec chorespec-postgres pg_dump -U chorespec_admin chorespec > chorespec-backup.sql
   ```
2. Upload the new `docker-compose.yml`, and `.env.example` renamed to `.env`, into the app folder.
3. In `.env`, set the credentials your database **already uses**:
   ```
   POSTGRES_USER=chorespec_admin
   POSTGRES_PASSWORD=chorespec_password
   POSTGRES_DB=chorespec
   ```
4. Generate and paste the keys as in [Configure `.env`](#2-configure-env), step 2.
   Everyone has to log in once more after this update. From then on, logins survive updates.
5. Pull and restart:
   ```bash
   sudo docker-compose pull
   sudo docker-compose up -d
   ```

### Optional: replace the old default database password
`chorespec_password` was public in this repository, so it's worth changing it. With the app running:

```bash
NEW_PW=$(openssl rand -hex 24); echo "$NEW_PW"
sudo docker exec chorespec-postgres psql -U chorespec_admin -d chorespec -c "ALTER USER chorespec_admin PASSWORD '$NEW_PW';"
```

Then put the printed password into `POSTGRES_PASSWORD` in `.env` and run `sudo docker-compose up -d`
so the backend reconnects with it.

---

## Updates
To update the app when a new version is pushed to GitHub:

```bash
sudo docker-compose pull
sudo docker-compose up -d
```

## Troubleshooting

| Symptom (in `sudo docker-compose logs`) | Cause | Fix |
|---|---|---|
| `chorespec-postgres`: *superuser password is not specified* | No `.env`, or `POSTGRES_PASSWORD` is empty | Create `.env` next to `docker-compose.yml` (see above) |
| `chorespec-backend`: *password authentication failed* | `.env` credentials don't match the existing database | Use the credentials the database was created with (see [Upgrading](#upgrading-an-existing-installation)) |
| Logging in doesn't work when using plain `http://` | `COOKIE_SECURE=true`: the browser drops the HTTPS-only login cookie | Set `COOKIE_SECURE=false`, then `sudo docker-compose up -d` |
| Everyone is logged out after each update | `JWT_SECRET_KEY` not set in `.env` | Generate keys and add them to `.env` |
