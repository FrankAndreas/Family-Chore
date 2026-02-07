# Deploying ChoreSpec on Synology NAS (or any Docker system)

This guide explains how to deploy the Family Chore App using Docker images hosted on GitHub Container Registry (GHCR).

## Prerequisites
- A Synology NAS with "Container Manager" (Docker) installed.
- SSH access to your NAS (optional but easier).
- If the GitHub repository is **Private**, you need a GitHub Personal Access Token (PAT) with `read:packages` scope.

## Deployment Steps

### 1. Prepare Folder
Create a folder on your NAS (e.g., `/docker/chorespec`) and upload only the `docker-compose.yml` file.

### 2. Configure
The `docker-compose.yml` is pre-configured to use the images from `ghcr.io/frankandreas/`. You can use it as is.

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
- Select the folder/file.
- Click "Next" -> "Done".

### 4. Access the App
Open your browser and navigate to:
`http://<YOUR_NAS_IP>:8080`

---

## Initial Setup
The system automatically seeds a default Admin user on first startup.

- **Username (Nickname)**: `Admin`
- **PIN**: `1234`

**Note:** The app data (database) persists in the `chores_data` Docker volume.

## Updates
To update the app when a new version is pushed to GitHub:

```bash
sudo docker-compose pull
sudo docker-compose up -d
```
