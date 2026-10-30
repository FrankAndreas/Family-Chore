# Deploying ChoreSpec on Synology NAS (or any Docker system)

This guide explains how to deploy the Family Chore App using Docker images hosted on GitHub Container Registry (GHCR).

## Prerequisites
- A Synology NAS with "Container Manager" (Docker) installed.
- SSH access to your NAS (needed to generate keys).
- The family hub (FrankAndreas/family-hub) running on the NAS: logging in goes through it.
- If the GitHub repository is **Private**, you need a GitHub Personal Access Token (PAT) with `read:packages` scope.

## Choose a Setup

| | Postgres (`docker-compose.yml`) | SQLite (`docker-compose.sqlite.yml`) |
|---|---|---|
| Containers | database, backend, frontend | backend, frontend |
| Database | Postgres in a Docker volume | a single file in `./data` |
| Good for | larger installs, existing Postgres users | a home NAS; simplest to run and back up |

The sections below describe the Postgres setup; for SQLite, follow
[SQLite Setup](#sqlite-setup) instead. [Automatic Updates](#automatic-updates) work with both.

> **Upgrading an existing Postgres installation?** The app now needs a `.env` file next to
> `docker-compose.yml`. Follow [Upgrading an existing installation](#upgrading-an-existing-installation)
> before pulling new images, or Postgres will not start.

## Fresh Installation (Postgres)

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
2. **`VAPID_PRIVATE_KEY`, `VAPID_PUBLIC_KEY`**: generate both at once:
   ```bash
   sudo docker run --rm ghcr.io/frankandreas/family-chore-backend:latest python -m backend.generate_keys
   ```
   Paste the printed lines into `.env`, replacing the empty entries.
3. **`VAPID_CLAIMS_EMAIL`**: your email address, as `mailto:you@example.com`.
4. **`HUB_URL`, `HUB_PUBLIC_URL`**: the family hub, see [Logging in](#5-logging-in-the-family-hub).

> **Why the keys matter:** if they are left empty, the backend generates them inside the container.
> They are then replaced every time the container is recreated, which happens on every update, and
> push notifications stop working.

Keep `.env` private: it contains your database password and keys.

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

### 5. Logging in: the family hub
The app has no PINs of its own: the family logs in at the family hub (FrankAndreas/family-hub), which
runs on the same NAS, and opens the app at `https://chores.local.<domain>` (see
[HTTPS at Home](#https-at-home-recommended); the hub's login cookie only reaches addresses under
`local.<domain>`). In the hub's **Einstellungen → Apps**, give the chores tile the app key `chores` and
tick everyone who uses it. Names and languages come from the hub; a parent in the hub is **Admin** here,
and a child gets their game role (Contributor, Teenager, Child, ...) from a parent in **User
Management**. "Logout" logs out in the hub, and so in every family app. The **Family Dashboard** at
`/family-dashboard` still works without a login.

Someone the hub no longer gives the app is hidden with their points and history and gets no tasks,
until a parent deletes their data under **Removed in the family hub**.

**Switching an existing installation** to the hub: add `HUB_URL`, `HUB_PUBLIC_URL` and `HUB_APP_KEY` to
the backend's `environment:` in the NAS's compose file (as in the templates; a value only in `.env`
doesn't reach the container), remove `JWT_SECRET_KEY` and `COOKIE_SECURE`, set the values in `.env`,
then update. Before the first login, make sure every person exists in the hub with the same name, as a
parent if they're Admin here and as a child otherwise, and is ticked: each is linked to that hub
person at the first login, and only then, so their points stay theirs.

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

## SQLite Setup

A simpler setup without a database container: the data lives in one file, `data/chorespec.db`.

1. **Create a user for the app** (recommended). In DSM, **Control Panel → User & Group → Create** a user
   such as `chorespec`, with a random password and no application permissions. On the shared folder
   that holds the app folder (e.g. `docker`), give it **Read only** (or no access): the nightly update
   runs as root, so the app's user must not be able to change `compose.yaml` or `nas-update.sh`. It
   still writes its own folders, because it owns them. The backend container runs as this user, so
   the app's files belong to a real, unprivileged account. Look up its IDs over SSH:
   ```bash
   id chorespec    # e.g. uid=1031(chorespec) gid=100(users)
   ```
   Skip this step to run as the image's built-in user instead (999:999).
2. **Prepare the folder.** Create the app folder (e.g. `/volume1/docker/chorespec`), upload
   `docker-compose.sqlite.yml` into it **renamed to `compose.yaml`**, and change the port in it if 8080
   is taken. Then create the data folders, owned by the app's user:
   ```bash
   cd /volume1/docker/chorespec
   sudo mkdir -p data uploads backups
   sudo chown -R 1031:100 data uploads backups    # the IDs from step 1, or 999:999
   ```
3. **Create `.env`** with the user's IDs, the family hub and the keys, so push notifications survive updates:
   ```bash
   printf 'PUID=1031\nPGID=100\nHUB_URL=http://<NAS_IP>:8086\nHUB_PUBLIC_URL=https://home.local.<domain>\n' | sudo tee .env    # IDs from step 1
   sudo docker run --rm ghcr.io/frankandreas/family-chore-backend:latest python -m backend.generate_keys | sudo tee -a .env
   sudo chmod 600 .env
   ```
   Optionally add `VAPID_CLAIMS_EMAIL=mailto:you@example.com` and the SMTP settings (see `.env.example`).
4. **Start** with `sudo docker-compose up -d` (or as a Container Manager project on this folder) and
   log in as described in [Logging in](#5-logging-in-the-family-hub).

The folders hold everything worth keeping: `data/` (database), `uploads/` (task photos) and
`backups/` (the app's own nightly database copies).

> **Coming from an older SQLite compose file** with only a `./data` volume? Task photos and the
> app's own backups were stored inside the container and are lost on every update. Switch to the
> template above (keeping your `./data` folder and port), add the folders and `.env` from steps 1–3,
> and run `sudo docker-compose up -d`.

---

## HTTPS at Home (recommended)

HTTPS is needed for the family hub's login (its cookie only reaches `*.local.<domain>`), and on plain
`http://<NAS_IP>:<port>` **push notifications don't work on phones**: browsers allow them only on HTTPS pages. Taking task
photos works either way.

The NAS's own reverse proxy fixes this; nothing is opened to the internet. You need a certificate for
a name that points to the NAS's home address, e.g. a wildcard `*.local.<domain>` from Let's Encrypt
(issued with [acme.sh](https://github.com/acmesh-official/acme.sh) and a DNS record `*.local` →
`<NAS_IP>`, "DNS only", at your DNS provider). If another app on the NAS already uses such a
certificate, reuse it and start at step 1.

1. **Reverse proxy.** DSM: **Control Panel → Login Portal → Advanced → Reverse Proxy → Create**:

   | Source | Destination |
   |---|---|
   | HTTPS, `chores.local.<domain>`, port 443, **Enable HSTS** | HTTP, `localhost`, the app's port (8080, or e.g. 8888 if you changed it) |

2. **Certificate.** **Control Panel → Security → Certificate → Settings**: pick the wildcard
   certificate for the new entry.
3. **Open** `https://chores.local.<domain>` on each phone, save it to the home screen again (replacing
   the old shortcut), and allow notifications when asked.

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

1. pulls the backend and frontend images; if nothing is new, it only checks that the backend is healthy
   and stops,
2. backs up the database to `db-backups/`: Postgres with `pg_dump`, SQLite with its online-backup API
   (keeps at least the newest 5 and everything from the last 7 days; the backend runs migrations on start),
3. keeps the running images tagged as `:previous` for [rolling back](#rolling-back-an-update),
4. restarts the app and waits until the backend is healthy, logging to `logs/update.log`.

It finds the compose file by its usual names (`compose.yaml`, `docker-compose.yml`, ...) and never changes
it, `.env` or the database container. It also removes dangling
(untagged) Docker images to save space, including those of other projects on the NAS.

### Setup
1. Copy `scripts/nas-update.sh` into the app folder (next to the compose file) and make it executable:
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
#    Postgres:
gunzip -c db-backups/chorespec-YYYYMMDD-HHMMSS.sql.gz | sudo docker exec -i chorespec-postgres sh -c \
  'psql -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" && psql -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1'
#    SQLite:
sudo sh -c 'gunzip -c db-backups/chorespec-YYYYMMDD-HHMMSS.sqlite.gz > data/chorespec.db'

# 3. Start the previous version
sudo docker-compose up -d backend frontend
```

Re-enable the task once a fixed version is published.

### Deploying from your computer
To install the latest version right away, or to roll out a new version of `nas-update.sh`, run from a
checkout of this repository:

```bash
cp .deploy.env.example .deploy.env   # once; then set NAS_HOST and NAS_DIR in it
scripts/deploy-nas.sh
```

It shows how the NAS's `nas-update.sh` differs from the repository's, uploads it after you confirm, and
runs the update. Add `--force` to restart the app even without a new version, e.g. after editing the
compose file on the NAS. The compose file and `.env` belong to your deployment and are never copied.

- **SSH** must be enabled on the NAS (**Control Panel → Terminal & SNMP → Enable SSH**). Connect once by
  hand (`ssh user@<NAS_IP>`) to verify and accept the NAS's host key; the script never accepts unknown keys.
- **Password:** without further setup, ssh and sudo ask for it. To avoid typing it, set `NAS_PASS_CMD` in
  `.deploy.env` to a command that prints it, e.g. `NAS_PASS_CMD=pass show nas` for the
  [pass](https://www.passwordstore.org/) password manager. The password is piped straight to ssh and
  `sudo` and never stored, shown or logged.
- `.deploy.env` is gitignored, so your NAS address stays out of the repository.

## Troubleshooting

| Symptom (in `sudo docker-compose logs`) | Cause | Fix |
|---|---|---|
| `chorespec-postgres`: *superuser password is not specified* | No `.env`, or `POSTGRES_PASSWORD` is empty | Create `.env` next to `docker-compose.yml` (see above) |
| `chorespec-backend`: *password authentication failed* | `.env` credentials don't match the existing database | Use the credentials the database was created with (see [Upgrading](#upgrading-an-existing-installation)) |
| The app keeps sending you to the family hub | The app isn't opened at `https://chores.local.<domain>`, or the hub's `COOKIE_DOMAIN` is missing | Open the app at its `local.<domain>` address; check the hub's `COOKIE_DOMAIN=local.<domain>` |
| "No access" after logging in at the hub | The chores tile in the hub has no app key `chores`, or the person isn't ticked | Fix it in the hub's **Einstellungen → Apps** |
| Email from Task Scheduler: *up to date, but the backend is stopped* | The app was stopped (by hand, or in Container Manager) | Start it with `sudo docker-compose up -d` in the app folder, or disable the task while it should stay off |
| Email from Task Scheduler: *up to date, but the backend is not healthy* | The backend keeps crashing without an update, e.g. after a change to `.env` (wrong `PUID`/`PGID`) | Check `logs/update.log`, fix the cause, then `sudo docker-compose up -d` and `sudo docker restart chorespec-frontend` |
| Email from Task Scheduler: *backend not healthy* | A new version fails to start | Check `logs/update.log` (it ends with the backend's log), then [roll back](#rolling-back-an-update) |
