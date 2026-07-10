# GoDaddy cPanel Deployment

This is a FastAPI app configured for GoDaddy/cPanel Python App through Phusion Passenger.

## Upload Location

Upload the project files into the Python app root:

```text
/home/dlhdga5t29co/noyyalexpress
```

The folder should contain `main.py` directly. Do not upload a nested `Noyyal Express Platform` folder.

Upload these files and folders:

```text
main.py
passenger_wsgi.py
requirements.txt
database.py
models.py
schemas.py
routes/
templates/
static/
utils/
```

Do not upload:

```text
.git/
__pycache__/
*.pyc
database_backup/
```

## cPanel Python App Settings

Use these values in **Setup Python App**:

```text
Python version: Python 3.x
Application root: noyyalexpress
Application URL: noyyalexpress.com
Application startup file: passenger_wsgi.py
Application entry point: application
```

## Environment Variables

Add these environment variables in the Python App screen:

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_godaddy_database_user
DB_PASSWORD=your_godaddy_database_password
DB_NAME=noyyalexpress
```

The database and tables must already exist in cPanel/phpMyAdmin.

For local development, copy `.env.example` to `.env` and fill in your local MySQL credentials. The app loads `.env` automatically when it exists:

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_local_database_user
DB_PASSWORD=your_local_database_password
DB_NAME=noyyalexpress
```

## Install Dependencies

In **Configuration files**, add:

```text
requirements.txt
```

Then click **Run Pip Install**. If terminal access is available, this is equivalent to:

```bash
pip install -r requirements.txt
```

Restart the Python app after installing dependencies.

## Quick Checks

If the site fails after deployment:

- Confirm `main.py` and `passenger_wsgi.py` are directly inside `/home/dlhdga5t29co/noyyalexpress`.
- Confirm the app is using Python 3.x, not Python 2.7.
- Confirm the DB user is assigned to the `noyyalexpress` database.
- Confirm `static/uploads/` exists if news images are referenced by database rows.
- Check the Passenger log file in cPanel for the exact error.
