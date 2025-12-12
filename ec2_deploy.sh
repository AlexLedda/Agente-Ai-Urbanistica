#!/bin/bash

# EC2 Deployment Script for Urbanistica AI Agent
# Usage: ./ec2_deploy.sh

echo "🚀 Starting Deployment Process..."

# 1. Update System
echo "🔄 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker & Git (if not present)
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker ubuntu
    echo "✅ Docker installed."
else
    echo "✅ Docker already installed."
fi

if ! command -v git &> /dev/null; then
    echo "📦 Installing Git..."
    sudo apt-get install -y git
    echo "✅ Git installed."
fi

# 3. Clone or Pull Repository
REPO_DIR="Agente-Ai-Urbanistica"
REPO_URL="https://github.com/AlexLedda/Agente-Ai-Urbanistica.git"

if [ -d "$REPO_DIR" ]; then
    echo "📂 Repository exists. Pulling latest changes..."
    cd $REPO_DIR
    git pull origin main
else
    echo "📂 Cloning repository..."
    git clone $REPO_URL
    cd $REPO_DIR
fi

# 4. Create Environment File (Dummy values for now, user should edit)
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat <<EOF > .env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_AI_API_KEY=your_google_key_here
EOF
    echo "⚠️  PLEASE EDIT .env with actual API keys!"
fi

# 5. Build and Start Containers
echo "🏗️  Building and starting containers..."
# We need to use sudo unless the user has re-logged in after adding to docker group
sudo docker compose down
sudo docker compose up --build -d

echo "✅ Deployment Complete!"
echo "🌐 Access the app at http://$(curl -s ifconfig.me)"
