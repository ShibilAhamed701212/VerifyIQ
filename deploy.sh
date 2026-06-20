#!/usr/bin/env bash
set -euo pipefail

IMAGE="verifyiq:latest"
CONTAINER="verifyiq"
DATASET_DIR="$(pwd)/dataset"
OUTPUT_DIR="$(pwd)/output"

echo "==> Building Docker image..."
docker build -t "$IMAGE" .

echo "==> Stopping and removing existing container (if any)..."
docker rm -f "$CONTAINER" 2>/dev/null || true

mkdir -p "$OUTPUT_DIR"

echo "==> Starting container..."
docker run -d \
  --name "$CONTAINER" \
  -p 8000:8000 \
  -v "$DATASET_DIR:/app/dataset:ro" \
  -v "$OUTPUT_DIR:/app/output" \
  -e GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}" \
  -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
  "$IMAGE"

echo "==> Waiting for health check..."
for i in $(seq 1 12); do
  sleep 5
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "Container is healthy!"
    exit 0
  fi
  echo "  Attempt $i/12..."
done

echo "WARNING: Health check did not pass within 60s. Container may still be starting."
echo "Check logs: docker logs $CONTAINER"

cleanup() {
  echo "==> Shutting down container..."
  docker stop "$CONTAINER" 2>/dev/null || true
  docker rm "$CONTAINER" 2>/dev/null || true
  echo "Container stopped and removed."
}
trap cleanup EXIT
