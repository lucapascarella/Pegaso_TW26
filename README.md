# SensorHub

Companion code for the *Tecnologie Web* milestones (live sessions, Università Telematica Pegaso).
Case study: AltraNodes S.r.l. builds a monitoring platform for the greenhouses of Serre Bellini.

## Milestone tags

| Tag | Content |
|-----|---------|
| `tw1-start` | Minimal FastAPI app + settings |
| `tw1-end` | Devices router (in-memory), validation, custom errors, `requests.http` |

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
