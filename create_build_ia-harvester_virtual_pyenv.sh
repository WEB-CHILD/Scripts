#!/usr/bin/env bash

set -euo pipefail

# -----------------------------
# Configuration
# -----------------------------
PYTHON_VERSION="3.13.7"
REPO_IAE="https://github.com/WEB-CHILD/InternetArchiveExtractor.git"
REPO_WAYBACK="https://github.com/WEB-CHILD/python-wayback-machine-downloader.git"

# -----------------------------
# Derived values
# -----------------------------
BASE_DIR="$(pwd)"
FOLDER_NAME="$(basename "$BASE_DIR")"
VENV_NAME="IA-Extractor_${FOLDER_NAME}"
WAYBACK_DIR="${BASE_DIR}/python-wayback-machine-downloader"

# -----------------------------
# Clone repositories
# -----------------------------
echo "Cloning repositories..."
git clone "$REPO_IAE"
git clone "$REPO_WAYBACK"

# -----------------------------
# Create and activate virtualenv
# -----------------------------
echo "Creating pyenv virtualenv: ${VENV_NAME}"
pyenv virtualenv "$PYTHON_VERSION" "$VENV_NAME"
pyenv local "$VENV_NAME"


# -----------------------------
# Install python-wayback-machine-downloader
# -----------------------------
echo "Installing python-wayback-machine-downloader..."
cd "$WAYBACK_DIR"
pip install .
cd "$BASE_DIR"

# -----------------------------
# Patch requirements.txt
# -----------------------------
echo "Updating InternetArchiveExtractor requirements.txt..."

REQ_FILE="${BASE_DIR}/InternetArchiveExtractor/requirements.txt"
WAYBACK_PATH="pywaybackup @ file://${WAYBACK_DIR}"

# Bakcup requirements.txt before replacing any existing pywaybackup line
sed -i.bak \
    -E "s|^pywaybackup.*|${WAYBACK_PATH}|" \
    "$REQ_FILE"

# -----------------------------
# Install InternetArchiveExtractor dependencies
# -----------------------------
echo "Installing InternetArchiveExtractor requirements..."
cd "${BASE_DIR}/InternetArchiveExtractor"
pip install -r requirements.txt

echo "Virtualenv '${VENV_NAME}' is ready and repos are built."

