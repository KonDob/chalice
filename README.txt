Project: Chalice + MongoDB (local dev)

Prerequisites
- Python 3.10+
- Virtualenv (optional but recommended)
- Docker (for local MongoDB)

Setup
1) Clone/open the project folder.
2) Create and activate a venv (recommended):
   python3 -m venv venv
   source venv/bin/activate
3) Install dependencies:
   pip install -r requirements.txt

MongoDB (local, no-auth)
A) Start ephemeral container (data not persisted):
   sudo docker run -d --name mongo -p 27017:27017 mongo:7

B) Start with persistent volume:
   sudo docker stop mongo && sudo docker rm mongo  # if previously created
   sudo docker run -d --name mongo -p 27017:27017 -v mongo_data:/data/db mongo:7

Connection settings (already configured for local)
- File: helloworld/.chalice/config.json
- MONGODB_URI: mongodb://localhost:27017
- MONGODB_DB: test

Run the API locally (Chalice)
1) Ensure venv is active (source venv/bin/activate).
2) From the helloworld/ directory:
   chalice local
3) Test health:
   curl http://127.0.0.1:8000/db/ping
   -> {"ok": true}

Seed data and query
- Seed 10 random cars:
  curl -X POST http://127.0.0.1:8000/cars/seed
- List cars:
  curl "http://127.0.0.1:8000/cars"
- List with filters (examples):
  curl "http://127.0.0.1:8000/cars?make=Toyota"
  curl "http://127.0.0.1:8000/cars?year=2018"
  curl "http://127.0.0.1:8000/cars?make=BMW&model=X5"
  curl "http://127.0.0.1:8000/cars?id=<uuid>"
- Average price (optionally filtered):
  curl "http://127.0.0.1:8000/cars/avg-price"
  curl "http://127.0.0.1:8000/cars/avg-price?make=Audi"

Debugging (PyCharm)
- Open the project in PyCharm.
- Configure a Run/Debug configuration:
  Script: <venv>/bin/chalice
  Parameters: local
  Working directory: helloworld/
  Environment: inherits shell (MONGODB_URI and MONGODB_DB are set via config.json)
- Set a breakpoint in helloworld/app.py (e.g., a route) and start Debug.

Notes
- If chalice is not found, install it: pip install chalice
- If Docker requires sudo, prefix commands with sudo.
- If you deploy to AWS API Gateway, note the stage prefix in URLs (default: /api), e.g. /api/db/ping.
