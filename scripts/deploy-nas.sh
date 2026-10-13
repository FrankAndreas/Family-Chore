#!/bin/bash
# Deploy ChoreSpec to the NAS from this machine, over SSH.
#
# Copies docker-compose.yml and nas-update.sh to the NAS (showing a diff and
# asking first), then runs the update there and shows the result. Use it for
# docker-compose.yml changes; image updates also arrive via the nightly task.
#
# Usage:   NAS_HOST=admin@nas.local scripts/deploy-nas.sh [--yes]
# Env:     NAS_HOST  SSH target (user@host or an alias from ~/.ssh/config), required
#          NAS_DIR   app folder on the NAS (default: /volume1/docker/chorespec)
# Options: --yes     don't ask for confirmation
#
# .env is never copied; edit it on the NAS (it holds the secrets).

set -euo pipefail

NAS_DIR="${NAS_DIR:-/volume1/docker/chorespec}"
ASSUME_YES=0
for arg in "$@"; do
    case "$arg" in
        --yes|-y) ASSUME_YES=1 ;;
        -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done
[ -n "${NAS_HOST:-}" ] || { echo "Set NAS_HOST, e.g. NAS_HOST=admin@nas.local $0" >&2; exit 2; }

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

confirm() {
    [ "$ASSUME_YES" -eq 1 ] && return 0
    read -r -p "$1 [y/N] " answer
    [[ "$answer" =~ ^[Yy]$ ]]
}

if ! git diff --quiet HEAD -- docker-compose.yml scripts/nas-update.sh \
    || [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main 2>/dev/null)" ]; then
    echo "Note: deploying files that differ from origin/main (uncommitted changes or another branch)."
    confirm "Continue anyway?" || exit 1
fi

echo "Connecting to $NAS_HOST ..."
ssh "$NAS_HOST" "test -d '$NAS_DIR'" || { echo "Folder $NAS_DIR not found on $NAS_HOST" >&2; exit 1; }
ssh "$NAS_HOST" "test -f '$NAS_DIR/.env'" || {
    echo "No .env in $NAS_DIR on the NAS. Create it first (see README_DOCKER.md)." >&2; exit 1; }

# Upload a file if it changed; returns 0 if it was uploaded
upload_if_changed() {
    local local_file=$1 remote_file="$NAS_DIR/$2" mode=$3
    if ssh "$NAS_HOST" "cat '$remote_file' 2>/dev/null" | diff -u --label "NAS: $2" --label "local: $2" - "$local_file"; then
        echo "$2: unchanged"
        return 1
    fi
    confirm "Upload the changes to $2 above?" || { echo "Aborted." >&2; exit 1; }
    ssh "$NAS_HOST" "cat > '$remote_file.tmp' && chmod $mode '$remote_file.tmp' && mv '$remote_file.tmp' '$remote_file'" < "$local_file"
    echo "$2: uploaded"
}

compose_changed=0
upload_if_changed docker-compose.yml docker-compose.yml 644 && compose_changed=1
upload_if_changed scripts/nas-update.sh nas-update.sh 755 || true

force=""
[ "$compose_changed" -eq 1 ] && force="--force"
echo "Running the update on the NAS (sudo may ask for your NAS password) ..."
ssh -t "$NAS_HOST" "sudo '$NAS_DIR/nas-update.sh' $force '$NAS_DIR'"
