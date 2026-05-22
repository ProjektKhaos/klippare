#!/usr/bin/env bash
set -e

# create_service.sh
# Skapar systemd-service för Gunicorn-processen. Ⓐ Style

PROJECT_DIR="${KLIPPARE_PROJECT_DIR:-/var/www/klippare}"
SERVICE_NAME="${KLIPPARE_SERVICE_NAME:-klippare}"
PORT="${KLIPPARE_PORT:-8000}"
RUN_USER="${KLIPPARE_RUN_USER:-administrator}"
RUN_GROUP="${KLIPPARE_RUN_GROUP:-www-data}"
DOMAIN="${KLIPPARE_DOMAIN:-example.com}"

sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<SERVICE
[Unit]
Description=Klippare Flask/OpenCV app
After=network.target

[Service]
User=${RUN_USER}
Group=${RUN_GROUP}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${PROJECT_DIR}/venv/bin"
Environment="KLIPPARE_DOMAIN=${DOMAIN}"
ExecStart=${PROJECT_DIR}/venv/bin/python -m gunicorn --workers 2 --bind 127.0.0.1:${PORT} app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
echo "${SERVICE_NAME}.service skapad. Starta med: sudo systemctl enable --now ${SERVICE_NAME}"
