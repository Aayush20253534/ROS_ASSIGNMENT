#!/usr/bin/env bash
#
# start.sh - one-command startup script for macOS / Linux.
#
# It checks that Docker is installed and running, then builds and launches
# everything with docker compose.

set -e

# 1. Is the docker command available at all?
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed."
  echo "Please install Docker Desktop: https://www.docker.com/products/docker-desktop/"
  exit 1
fi

# 2. Is the Docker daemon actually running? `docker info` fails if it is not.
if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop and run this script again."
  exit 1
fi

# 3. Build and start both containers. --build ensures the ROS image is up to date.
echo "Starting ROS 2 + React starter..."
echo "Once running, open http://localhost:5173 in your browser."
docker compose up --build
