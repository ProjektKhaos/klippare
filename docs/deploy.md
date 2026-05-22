# Deploy för Klippare

Kör från projektkatalogen:

```bash
cd /var/www/klippare
bash scripts/install_server.sh
bash scripts/create_service.sh
bash scripts/create_apache_vhost.sh
```

Starta och kontrollera tjänsten:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now klippare
sudo systemctl status klippare
curl http://127.0.0.1:8000/health
```

När DNS pekar till servern, kör:

```bash
sudo certbot --apache -d example.com
```

Välj HTTPS-redirect om Certbot frågar.
