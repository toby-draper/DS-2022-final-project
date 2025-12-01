#!/usr/bin/env bash

# Build the Docker image
docker build -t final-project-app:latest .

# Run the container
docker run --rm -p 8000:8000 --env-file .env.example final-project-app:latest

# Optional health check
curl http://localhost:8000/health
