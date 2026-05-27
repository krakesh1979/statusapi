# Status Poll API

Simple Flask API to test async job polling from an external public endpoint.

## Local setup

```bash
cd /Users/rakeshkumar/Documents/repository/statuspoll
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Test locally

Health check:

```bash
curl http://localhost:5000/
```

Start a job:

```bash
curl -X POST http://localhost:5000/api/jobs/123/start
```

Poll status:

```bash
curl http://localhost:5000/api/jobs/123/status
```

## Deploy to Render

1. Push this folder to GitHub.
2. Go to Render and create a new Web Service.
3. Connect the GitHub repo.
4. Use these settings:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

## Deploy to Railway

1. Push this folder to GitHub.
2. Create a Railway project from GitHub.
3. Railway should detect Python automatically.
4. Use `gunicorn app:app` as the start command if needed.
5. Generate a public domain from Railway networking settings.

## Production note

This demo stores job state in memory. For production, use Redis, PostgreSQL, MongoDB, DynamoDB, or another persistent store.
