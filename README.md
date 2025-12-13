# Employee Referral System

This is a simple Flask-based referral/signup system. The frontend uses plain HTML/CSS/JS in `templates/` and `static/`. The backend is Python/Flask and uses SQLAlchemy for the database.

Goal: Use a cloud-hosted Postgres (e.g., Supabase, Heroku Postgres) so the database lives in the cloud and multiple users can access the app via a hosted backend URL.

Quick setup (local):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` file (see `.env.example`) and set `DATABASE_URL` and `SECRET_KEY`.

3. Run the app:

```powershell
python app.py
```

Using a cloud Postgres (Supabase example):

- Create a free Supabase project and get the Postgres connection string (Settings → Database → Connection string).
- Copy the connection string into `DATABASE_URL` in your `.env` file. If the string starts with `postgres://`, the app will auto-normalize it to `postgresql://` for SQLAlchemy.
- Restart the app; tables will be created automatically by SQLAlchemy on first run.

Notes:
- This repository currently provides a simple backend. To make the whole app publicly accessible you will need to deploy the backend (e.g., to Render, Fly.io, Railway, Heroku, or a VM) and serve the static frontend or configure a static host.
- If you want, I can help deploy the backend and/or host the frontend so you get a public link for users to login and add new users.
