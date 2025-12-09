#!/bin/bash

# Configuration
HOST="34.203.191.130"
USER="ubuntu"
KEY="./urban-key.pem"
DEST="/home/ubuntu/urban-ai"

# Check if key exists
if [ ! -f "$KEY" ]; then
    echo "Error: Key file $KEY not found!"
    exit 1
fi

echo "======================================================="
echo " Deploying Urbanistica AI Agent to AWS ($HOST)"
echo "======================================================="

# Set key permissions
chmod 400 "$KEY"

# 1. Create remote directory
echo "[1/3] Creating remote directory..."
ssh -i "$KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "mkdir -p $DEST"

# 2. Sync files
echo "[2/3] Syncing files (excluding large files and artifacts)..."
rsync -avz --progress -e "ssh -i $KEY -o StrictHostKeyChecking=no" \
    --exclude '.git' \
    --exclude '.github' \
    --exclude '.idea' \
    --exclude '.vscode' \
    --exclude 'node_modules' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '*.DS_Store' \
    --exclude '*.tar.gz' \
    --exclude '*.zip' \
    --exclude 'backend_part_*' \
    --exclude 'logs/*' \
    --exclude 'frontend/dist' \
    . "$USER@$HOST:$DEST"

echo "[3/3] Deployment files transferred."
echo "======================================================="
echo "Status: READY TO LAUNCH"
echo ""
echo "To finish setup, run these commands:"
echo ""
echo "1. Connect to server:"
echo "   ssh -i $KEY $USER@$HOST"
echo ""
echo "2. Go to directory:"
echo "   cd urban-ai"
echo ""
echo "3. Start Docker:"
echo "   sudo docker-compose up -d --build"
echo ""
echo "4. Check logs:"
echo "   sudo docker-compose logs -f"
echo "======================================================="
