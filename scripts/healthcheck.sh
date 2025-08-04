#!/bin/bash
# Healthcheck script that uses the PORT environment variable
PORT=${PORT:-8000}
curl -f http://localhost:${PORT}/ || exit 1
