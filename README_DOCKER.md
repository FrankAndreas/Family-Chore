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
New versions are published as `latest` whenever a change is merged to `main` and CI passes.
Set up [Automatic Updates](#automatic-updates) to install them nightly, or update by hand:

```bash
sudo docker-compose pull
sudo docker-compose up -d
```

## Automatic Updates

`scripts/nas-update.sh` checks for new app images and installs them. Run nightly by DSM's Task Scheduler, it:

1. pulls the backend and frontend images and stops if nothing is new,
2. backs up the database to `db-backups/` (keeps at least the newest 5 and everything from the last 7 days; the backend runs migrations on start),
3. keeps the running images tagged as `:previous` for [rolling back](#rolling-back-an-update),
4. restarts the app and waits until the backend is healthy, logging to `logs/update.log`.

It never changes `docker-compose.yml`, `.env` or the Postgres container; deploy those deliberately
(see [Deploying from your computer](#deploying-from-your-computer)). It also removes dangling
(untagged) Docker images to save space, including those of other projects on the NAS.

### Setup
1. Copy `scripts/nas-update.sh` into the app folder (next to `docker-compose.yml`) and make it executable:
   ```bash
   sudo chmod +x /volume1/docker/chorespec/nas-update.sh
   ```
2. Run it once by hand and check that it ends with "Up to date" or "Update complete":
   ```bash
   sudo /volume1/docker/chorespec/nas-update.sh
   ```
3. In DSM, open **Control Panel → Task Scheduler → Create → Scheduled Task → User-defined script**:
   - **General**: any name (e.g. `ChoreSpec update`), user **root**
   - **Schedule**: daily, at a quiet time (e.g. 03:30)
   - **Task Settings**: tick **Send run details by email** and **only when the script terminates abnormally**,
     and enter the command:
     ```bash
     bash /volume1/docker/chorespec/nas-update.sh
     ```

If the GitHub repository is private, log in to the registry once **as root**, since the task runs as root:
`sudo docker login ghcr.io -u <github-user>` with a token that has `read:packages`.

### Rolling back an update
If a new version misbehaves, go back to the previous one. First **disable the scheduled task**,
otherwise the next night installs the same version again. Then, in the app folder:

```bash
cd /volume1/docker/chorespec
# 1. Point latest at the previous images (frontend only if it was updated; see logs/update.log)
sudo docker tag ghcr.io/frankandreas/family-chore-backend:previous ghcr.io/frankandreas/family-chore-backend:latest
sudo docker tag ghcr.io/frankandreas/family-chore-frontend:previous ghcr.io/frankandreas/family-chore-frontend:latest

# 2. Restore the database from the backup taken right before the update
#    (the new version may have migrated it). Changes made since the update are lost.
sudo docker stop chorespec-backend
gunzip -c db-backups/chorespec-YYYYMMDD-HHMMSS.sql.gz | sudo docker exec -i chorespec-postgres sh -c \
  'psql -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" && psql -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1'

# 3. Start the previous version
sudo docker-compose up -d backend frontend
```

Re-enable the task once a fixed version is published.

### Deploying from your computer
For changes to `docker-compose.yml`, or to update right away, run from a checkout of this repository:

```bash
NAS_HOST=admin@<YOUR_NAS_IP> scripts/deploy-nas.sh
```

It shows what differs from the NAS's `docker-compose.yml` and `nas-update.sh`, uploads them after you
confirm, and runs the update (restarting the app if the compose file changed). It needs SSH access to
the NAS (**Control Panel → Terminal & SNMP → Enable SSH**); set `NAS_DIR` if the app folder isn't
`/volume1/docker/chorespec`. `.env` is never copied; edit it on the NAS.

## Troubleshooting

| Symptom (in `sudo docker-compose logs`) | Cause | Fix |
|---|---|---|
| `chorespec-postgres`: *superuser password is not specified* | No `.env`, or `POSTGRES_PASSWORD` is empty | Create `.env` next to `docker-compose.yml` (see above) |
| `chorespec-backend`: *password authentication failed* | `.env` credentials don't match the existing database | Use the credentials the database was created with (see [Upgrading](#upgrading-an-existing-installation)) |
| Logging in doesn't work when using plain `http://` | `COOKIE_SECURE=true`: the browser drops the HTTPS-only login cookie | Set `COOKIE_SECURE=false`, then `sudo docker-compose up -d` |
| Everyone is logged out after each update | `JWT_SECRET_KEY` not set in `.env` | Generate keys and add them to `.env` |
| Email from Task Scheduler: *backend not healthy* | A new version fails to start | Check `logs/update.log` (it ends with the backend's log), then [roll back](#rolling-back-an-update) |
