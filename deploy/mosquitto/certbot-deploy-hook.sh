#!/bin/sh
# /etc/letsencrypt/renewal-hooks/deploy/mosquitto.sh
# Copy the renewed certificate where the mosquitto user can read it, then reload the broker.
set -e
DOMAIN=serre.example.it
install -m 644 -o mosquitto /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/mosquitto/certs/fullchain.pem
install -m 600 -o mosquitto /etc/letsencrypt/live/$DOMAIN/privkey.pem   /etc/mosquitto/certs/privkey.pem
systemctl reload mosquitto
