# 🚀 ReNote — Production Deployment Guide

This guide provides step-by-step instructions for deploying **ReNote** to modern cloud hosting platforms like **Render**, **Railway**, or any standard Linux VPS.

---

## 🏗️ Architecture Overview

- **Framework**: Django 5.2 (Python 3.12 / 3.13)
- **WSGI Application Server**: [Gunicorn](https://gunicorn.org/) (`gunicorn renote.wsgi:application`)
- **Static Assets**: [WhiteNoise](https://whitenoise.readthedocs.io/) (compresses, hashes, and serves static files directly from Python)
- **Database**: PostgreSQL (managed via `dj-database-url` and `psycopg2-binary`)
- **Process Manager**: `Procfile` and `build.sh`
- **Cache**: Django in-memory LocMemCache (caches API queries and catalog lookups)
- **Email**: Django SMTP backend (for transactional password reset links)

---

## 📋 Required Environment Variables

When deploying to production, configure these variables in your hosting provider's dashboard:

| Variable | Description | Required? | Example Value |
| :--- | :--- | :---: | :--- |
| `SECRET_KEY` | Unique cryptographic key for signing sessions and tokens. | **Yes** | *(Generate a 50+ char random string)* |
| `DEBUG` | Disables debug mode in production. | **Yes** | `False` |
| `ALLOWED_HOSTS` | Comma-separated domains allowed to serve requests. | **Yes** | `renote.onrender.com,renote.app` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated full HTTPS origins for CSRF protection. | **Yes** | `https://renote.onrender.com,https://renote.app` |
| `DATABASE_URL` | PostgreSQL connection URI. | **Yes** | `postgresql://user:pass@host:5432/dbname` |
| `TMDB_API_KEY` | *(Optional)* The Movie Database API key (v3 auth) for movie metadata. | Optional | `your_tmdb_api_key` |
| `EMAIL_BACKEND` | Django email backend class. | **Yes** | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | SMTP server host. | **Yes** | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port. | **Yes** | `587` |
| `EMAIL_USE_TLS` | Enable TLS encryption. | **Yes** | `True` |
| `EMAIL_HOST_USER` | Sending email address. | **Yes** | `renote.app.official@gmail.com` |
| `EMAIL_HOST_PASSWORD` | App-specific password or API token. | **Yes** | `abcd efgh ijkl mnop` |
| `DEFAULT_FROM_EMAIL` | Friendly sender name and address displayed to users. | **Yes** | `ReNote <renote.app.official@gmail.com>` |

> 💡 **Tip — Generate a Secure Secret Key:**  
> Run this in your terminal to generate a secure key:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 🚀 Option 1: Deploying to Render (Recommended)

Render offers free hosting for web services and PostgreSQL databases with automatic deployments on Git push.

### Step 1: Create a PostgreSQL Database
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **PostgreSQL**.
3. Name: `renote-db`
4. Region: Choose the region closest to your users (e.g. `Singapore`, `Oregon`, `Frankfurt`).
5. Click **Create Database**.
6. Once provisioned, copy the **Internal Database URL** (or **External Database URL** if hosting database elsewhere like Supabase).

### Step 2: Create the Web Service
1. In the Render Dashboard, click **New +** -> **Web Service**.
2. Connect your GitHub repository: `venzblanz/ReNote`.
3. Configure settings:
   - **Name**: `renote`
   - **Branch**: `testing` (or `main`)
   - **Region**: Same region as your database
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn renote.wsgi:application`
   - **Plan**: `Free`

### Step 3: Add Environment Variables
Under the **Environment** tab of your new Web Service, add:
- `SECRET_KEY`: *(paste your generated random key)*
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `renote.onrender.com,127.0.0.1` *(replace with your actual Render URL)*
- `CSRF_TRUSTED_ORIGINS`: `https://renote.onrender.com`
- `DATABASE_URL`: *(paste the PostgreSQL URL from Step 1)*
- `EMAIL_BACKEND`: `django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST`: `smtp.gmail.com`
- `EMAIL_PORT`: `587`
- `EMAIL_USE_TLS`: `True`
- `EMAIL_HOST_USER`: `your_email@gmail.com`
- `EMAIL_HOST_PASSWORD`: `your_16_character_app_password`
- `DEFAULT_FROM_EMAIL`: `ReNote <your_email@gmail.com>`

### Step 4: Deploy & Create Admin Superuser
1. Click **Create Web Service**. Render will automatically run `./build.sh` (installing dependencies, compiling static files, running database migrations) and start Gunicorn.
2. Once the deploy status is **Live**, open the **Shell** tab in the Render dashboard and create your admin account:
   ```bash
   python manage.py createsuperuser
   ```

---

## 🚂 Option 2: Deploying to Railway

Railway automatically detects `Procfile` and provides instant zero-configuration deploys.

1. Go to [Railway.app](https://railway.app/) and click **New Project**.
2. Select **Deploy from GitHub repo** and choose `ReNote`.
3. Click **Add Plugin** -> **PostgreSQL**. Railway automatically injects `DATABASE_URL`.
4. Click your web service -> **Variables**, and add:
   - `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=*`, `CSRF_TRUSTED_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}`
   - Email SMTP credentials.
5. In **Settings**, generate a public domain (e.g. `renote-production.up.railway.app`).
6. Click **Deploy**. Railway will run `build.sh` and launch via `Procfile`.

---

## 🔒 Gmail SMTP Setup Checklist

To enable live password reset emails sent to users:

1. Create a dedicated Google Account (e.g. `renote.app.official@gmail.com`).
2. Go to [Google Account Security](https://myaccount.google.com/security) and enable **2-Step Verification**.
3. Go to [App Passwords](https://myaccount.google.com/apppasswords).
4. Enter `ReNote` under app name and click **Create**.
5. Copy the 16-character code into `EMAIL_HOST_PASSWORD` without spaces.

---

## ✅ Post-Deployment Verification

After deploying, verify the following in your live browser:

1. **Static Files & Avatars**: Check that the navbar logo, background gradients, and predefined avatar selection render properly with full styling.
2. **Registration & Login**: Create a new account and confirm instant redirection to the Dashboard.
3. **Catalog Search**: Go to `/library/add/` and search for an anime (e.g., *Solo Leveling*) or filter by genre to verify AniList/Kitsu live fetching and caching.
4. **Password Reset Flow**: Log out, click *"Forgot password?"*, enter your email, and confirm the recovery email arrives in your inbox with the custom ReNote card.
5. **SEO Directives**: Open `https://your-domain.com/robots.txt` and `https://your-domain.com/sitemap.xml` to verify crawler indexability.
6. **Custom Error Pages**: Visit `https://your-domain.com/non-existent-url` to ensure your celestial 404 error page displays with a working *"Back to Dashboard"* button.

---

## 🛠️ Common Troubleshooting

### 1. `DisallowedHost at /`
- **Cause**: The incoming domain is not in `ALLOWED_HOSTS`.
- **Fix**: Add your full domain (e.g. `my-app.onrender.com`) to `ALLOWED_HOSTS` in your environment variables dashboard.

### 2. `Forbidden (403): CSRF verification failed`
- **Cause**: Django 4+ requires explicit HTTPS origins for form POST requests.
- **Fix**: Ensure `CSRF_TRUSTED_ORIGINS` is set with the exact `https://` protocol (e.g. `https://my-app.onrender.com`).

### 3. Missing CSS/Static Files
- **Cause**: Static files were not collected.
- **Fix**: Confirm that your build command runs `python manage.py collectstatic --no-input` and that `whitenoise.middleware.WhiteNoiseMiddleware` is in `MIDDLEWARE`.
