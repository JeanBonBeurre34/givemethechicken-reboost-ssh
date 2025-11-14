#!/bin/bash

IMAGE_NAME="givemethechicken:latest"

CONTAINER_IDS=$(docker ps --filter "ancestor=${IMAGE_NAME}" --format "{{.ID}}")

if [ -z "$CONTAINER_IDS" ]; then
    echo "[+] No running container found for image: $IMAGE_NAME"
else
    echo "[+] Stopping containers running from $IMAGE_NAME ..."
    for ID in $CONTAINER_IDS; do
        echo "[+] Stopping $ID"
        docker stop "$ID"
    done
    echo "[+] Containers stopped."
fi

echo "[+] Cleaning SSH known_hosts entry for localhost..."
ssh-keygen -f "/home/regol/.ssh/known_hosts" -R "localhost"

echo "[+] Rebuilding Docker image: $IMAGE_NAME ..."
docker build -t "$IMAGE_NAME" .

echo "[+] Running new container on port 22..."
docker run -d -p 22:22 "$IMAGE_NAME"

echo "[+] Done!"

