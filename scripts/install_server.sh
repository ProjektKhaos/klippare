#!/usr/bin/env bash
set -e

# install_server.sh
# Installerar grundpaket för Klippare på Ubuntu 24.04. Ⓐ Style

sudo apt update
sudo apt install -y python3 python3-venv python3-pip apache2 certbot python3-certbot-apache

PROJECT_DIR="${KLIPPARE_PROJECT_DIR:-/var/www/klippare}"
WEB_USER="${KLIPPARE_WEB_USER:-administrator}"
WEB_GROUP="${KLIPPARE_WEB_GROUP:-www-data}"

cd "$PROJECT_DIR"

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p storage/uploads storage/results storage/zips
touch storage/uploads/.gitkeep storage/results/.gitkeep storage/zips/.gitkeep

sudo chown -R "$WEB_USER:$WEB_GROUP" "$PROJECT_DIR"
sudo chmod -R 775 "$PROJECT_DIR"

echo "Klippare installation klar."
