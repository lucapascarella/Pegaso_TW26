# SensorHub

Companion code for the *Tecnologie Web* milestones (live sessions, Università Telematica Pegaso).
Case study: AltraNodes S.r.l. builds a monitoring platform for the greenhouses of Serre Bellini.

## Milestone tags

| Tag | Content |
|-----|---------|
| `tw1-start` | Minimal FastAPI app + settings |
| `tw1-end` | Devices router (in-memory), validation, custom errors, `requests.http` |
| `tw2-start` | Same as tw1-end |
| `tw2-end` | SQLite persistence with SQLModel, CRUD layer, optimistic locking on device config |
| `tw3-start` | Same as tw2-end |
| `tw3-end` | Users, password hashing, JWT login, role-based access (admin / operator / viewer) |
| `tw4-start` | Same as tw3-end |
| `tw4-end` | MQTT bridge (paho-mqtt), telemetry storage, online/offline status, config resend, device simulator |
| `tw5-start` | Same as tw4-end |
| `tw5-end` | Server-Sent Events: live telemetry and status to the browser |
| `tw6-start` | Same as tw5-end |
| `tw6-end` | React frontend (Vite): login, device list |
| `tw7-start` | Same as tw6-end |
| `tw7-end` | Live dashboard (SSE), config form with 409 handling, CORS settings |
| `tw8-start` | Same as tw7-end |
| `tw8-end` | Production deploy: gunicorn, systemd, nginx, Mosquitto TLS + ACL, GitHub Actions CI |

```bash
git checkout tw1-start   # start of a milestone
git checkout tw1-end     # final state of a milestone
```

## Backend setup (Ubuntu / WSL)

```bash
sudo apt update && sudo apt install -y python3-venv
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
fastapi dev app.py        # http://127.0.0.1:8000/docs
```

> The database file `sensorhub.db` is created at startup. When a milestone changes the tables,
> delete it (`rm backend/sensorhub.db`) and restart: there are no migrations in the course code.

The first admin user is created at startup from `ADMIN_EMAIL` / `ADMIN_PASSWORD` in `.env`.

## MQTT broker and simulator

```bash
sudo apt install -y mosquitto mosquitto-clients
mosquitto -c deploy/mosquitto/dev.conf -v          # terminal 1: broker on :1883
cd simulator && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python simulator.py SH-000123                       # terminal 2: one simulated device
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev               # http://localhost:5173 (calls to /api are proxied to :8000)
```

## Production

See `deploy/README.md`.
