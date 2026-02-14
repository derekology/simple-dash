#!/bin/bash

# Simple Dash - Docker Start Script for Linux/Mac

set -e

echo "🚀 Starting Simple Dash..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. You can edit it to customize settings."
fi

# Build and start the containers
echo "🔨 Building Docker images..."
docker compose build

echo "🎯 Starting containers..."
docker compose up -d

# Wait for container to be healthy
echo "⏳ Waiting for container to be ready..."
sleep 5

# Check container status
if docker compose ps | grep -q "Up"; then
    echo "✅ Simple Dash is running!"
    echo ""
    echo "🌐 Access the application at: http://localhost:8000"
    echo ""
    echo "📊 Useful commands:"
    echo "  View logs:    docker compose logs -f"
    echo "  Stop:         docker compose down"
    echo "  Restart:      docker compose restart"
    echo "  Shell access: docker compose exec simpledash sh"
    echo ""
else
    echo "❌ Container failed to start. Check logs with: docker compose logs"
    exit 1
fi
