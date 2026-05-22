#!/usr/bin/env bash
set -e

# create_apache_vhost.sh
# Skapar Apache reverse proxy för Klippare. Ⓐ Style

DOMAIN="${KLIPPARE_DOMAIN:-example.com}"
PORT="${KLIPPARE_PORT:-8000}"
SITE_CONF="${DOMAIN}.conf"
LOG_NAME="${DOMAIN//./_}"

sudo tee "/etc/apache2/sites-available/${SITE_CONF}" > /dev/null <<VHOST
<VirtualHost *:80>
    ServerName ${DOMAIN}

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:${PORT}/
    ProxyPassReverse / http://127.0.0.1:${PORT}/

    ErrorLog \${APACHE_LOG_DIR}/${LOG_NAME}_error.log
    CustomLog \${APACHE_LOG_DIR}/${LOG_NAME}_access.log combined
</VirtualHost>
VHOST

sudo a2enmod proxy proxy_http headers rewrite
sudo a2ensite "$SITE_CONF"
sudo apache2ctl configtest
sudo systemctl reload apache2

echo "Apache vhost skapad och aktiverad."
