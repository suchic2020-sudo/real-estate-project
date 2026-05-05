# Apex Estates

A polished Flask real estate marketplace built with SQLite, secure authentication, admin property management, filters, and deployment support for Render.com.

## Features

- Secure password hashing with `werkzeug.security`
- Admin CRUD for properties with image upload and unique filenames
- Property search, filtering, and pagination
- Favorites system for signed-in users
- Flash messages for actions and polished UI
- Deployment-ready configuration, including `requirements.txt`, `Procfile`, and `.env.example`

## Local Setup

1. Create and activate your Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the environment example:
   ```bash
   copy .env.example .env
   ```
4. Set `SECRET_KEY` in `.env`.
5. Start the app:
   ```bash
   python app.py
   ```
6. Visit `http://127.0.0.1:5000`.

## Deploying to Render.com

1. Push this repository to GitHub.
2. Create a new Web Service on Render.
3. Connect the GitHub repository.
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add environment variables in Render:
   - `SECRET_KEY`
   - `DATABASE_URL` (optional, defaults to `database.db`)
   - `DEBUG` = `False`
6. Deploy.

## Admin Access

A default admin account is seeded automatically if none exists:

- Email: `admin@gmail.com`
- Password: `1234`

Please update the admin password in production.
