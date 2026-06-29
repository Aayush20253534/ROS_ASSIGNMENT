@echo off
REM start.bat - one-command startup script for Windows.
REM
REM Checks that Docker is installed and running, then builds and launches
REM everything with docker compose.

REM 1. Is the docker command available?
where docker >nul 2>nul
if errorlevel 1 (
    echo Docker is not installed.
    echo Please install Docker Desktop: https://www.docker.com/products/docker-desktop/
    exit /b 1
)

REM 2. Is the Docker daemon running? `docker info` returns an error if not.
docker info >nul 2>nul
if errorlevel 1 (
    echo Docker is not running. Start Docker Desktop and run this script again.
    exit /b 1
)

REM 3. Build and start both containers.
echo Starting ROS 2 + React starter...
echo Once running, open http://localhost:5173 in your browser.
docker compose up --build
