# Production deploy (Ubuntu 24.04)

Target: one server with a public IP (or a home server / Jetson Xavier reachable through DDNS and port forwarding).
Replace `serre.example.it` with the real domain everywhere.

```
Internet ──443──► nginx ──unix socket──► gunicorn (1 worker, uvicorn) ──► SQLite
         ──8883─► Mosquitto (TLS) ◄──1883 loopback── MQTT bridge
```

## 1. Base system and firewall

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx mosquitto mosquitto-clients python3-venv certbot python3-certbot-nginx git
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8883/tcp
sudo ufw enable
```

Port 8000 (uvicorn) and 1883 (plain MQTT) are **not** opened.

## 2. Application user and code

```bash
sudo useradd --system --home /opt/sensorhub --shell /usr/sbin/nologin sensorhub
sudo git clone https://github.com/<owner>/sensorhub.git /opt/sensorhub
sudo git -C /opt/sensorhub checkout tw8-end
cd /opt/sensorhub/backend
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
sudo mkdir -p /var/lib/sensorhub /etc/sensorhub
sudo chown sensorhub: /var/lib/sensorhub
sudo cp ../deploy/sensorhub.env.example /etc/sensorhub/sensorhub.env
sudo chown root:sensorhub /etc/sensorhub/sensorhub.env && sudo chmod 640 /etc/sensorhub/sensorhub.env
sudo nano /etc/sensorhub/sensorhub.env      # SECRET_KEY, ADMIN_PASSWORD, MQTT_PASSWORD
```

## 3. Frontend build

On the development machine (or on the server, with Node.js installed):

```bash
cd frontend && npm install && npm run build
sudo mkdir -p /var/www/sensorhub
sudo cp -r dist/* /var/www/sensorhub/
```

## 4. HTTPS certificate

```bash
sudo cp deploy/nginx/sensorhub.conf /etc/nginx/sites-available/sensorhub
sudo ln -s /etc/nginx/sites-available/sensorhub /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
# first certificate (nginx must answer on port 80 with the domain pointing to this server)
sudo certbot certonly --nginx -d serre.example.it
sudo nginx -t && sudo systemctl reload nginx
```

certbot installs a timer that renews the certificate automatically (`systemctl list-timers | grep certbot`).

## 5. Mosquitto with TLS and ACL

```bash
sudo cp deploy/mosquitto/prod.conf /etc/mosquitto/conf.d/sensorhub.conf
sudo cp deploy/mosquitto/acl /etc/mosquitto/acl
sudo mkdir -p /etc/mosquitto/certs
sudo cp deploy/mosquitto/certbot-deploy-hook.sh /etc/letsencrypt/renewal-hooks/deploy/mosquitto.sh
sudo /etc/letsencrypt/renewal-hooks/deploy/mosquitto.sh       # first copy of the certificate

# one user for the backend, one per device (username = serial)
sudo mosquitto_passwd -c /etc/mosquitto/passwd backend
sudo mosquitto_passwd /etc/mosquitto/passwd SH-000123
sudo chown root:mosquitto /etc/mosquitto/passwd /etc/mosquitto/acl
sudo chmod 640 /etc/mosquitto/passwd /etc/mosquitto/acl
sudo systemctl restart mosquitto
```

Test from outside:

```bash
python simulator.py SH-000123 --host serre.example.it --port 8883 --tls --username SH-000123 --password <pwd>
```

## 6. Backend service

```bash
sudo cp deploy/systemd/sensorhub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sensorhub
systemctl status sensorhub
journalctl -u sensorhub -f
curl https://serre.example.it/api/health
```

## 7. Update to a new version

```bash
cd /opt/sensorhub && sudo git fetch --tags && sudo git checkout <tag>
sudo backend/.venv/bin/pip install -r backend/requirements.txt
sudo systemctl restart sensorhub
```

## Production checklist

- [ ] `DEBUG=false`, random `SECRET_KEY`, admin password changed
- [ ] only ports 22, 80, 443, 8883 open (`sudo ufw status`)
- [ ] `https://` works and `http://` redirects
- [ ] `/docs` reachable only if wanted (otherwise restrict it in nginx)
- [ ] Mosquitto: `allow_anonymous false`, one user per device, ACL tested
- [ ] backup of `/var/lib/sensorhub/sensorhub.db` (e.g. nightly `sqlite3 .backup`)
- [ ] `/api/health` checked by an external monitor
