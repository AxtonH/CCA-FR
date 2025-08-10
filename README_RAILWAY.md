Deploying to Railway (Single Service: Flask serves React)
=========================================================

Prerequisites
-------------
- Railway account
- Railway CLI (optional)

Deploy Steps
------------
1. Push this repo to GitHub.
2. In Railway, create a new project → Deploy from GitHub → select this repo.
3. Railway will use Nixpacks to install Python and Node, then:
   - pip install -r requirements.txt
   - npm ci && npm run build (builds React to `build/`)
   - starts Flask (`python backend/run_backend.py`)
4. Set environment variables as needed (e.g., Odoo credentials) in Railway → Variables.

Service
-------
- Single web service runs: `python backend/run_backend.py`
- Flask serves API under `/api/*` and React static build under `/`.
- Binds to `PORT` provided by Railway.

Local testing (optional)
------------------------
- Build the frontend locally: `npm install && npm run build`
- Run backend: `python backend/run_backend.py`
- Visit http://localhost:8000

Health Check
------------
- Open Railway URL and hit `/api/health`.

