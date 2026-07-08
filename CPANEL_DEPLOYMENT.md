# cPanel Deployment Notes

This project is a FastAPI app. On cPanel, create it through **Setup Python App** and point the application root to this project folder.

## Required cPanel Settings

- Application startup file: `passenger_wsgi.py`
- Application entry point: `application`
- Application root: the folder containing `main.py`
- Application URL: your domain or subdomain

## Install Dependencies

In the cPanel Python app terminal, run:

```bash
pip install -r requirements.txt
```

Then restart the Python app from cPanel.

## 403 Forbidden Checklist

If the domain shows `403 Forbidden`:

- Confirm the domain is mapped to the Python app in cPanel.
- Confirm `passenger_wsgi.py` is in the application root.
- Confirm the startup file is `passenger_wsgi.py`.
- Confirm the entry point is `application`.
- Restart the Python app.
- Check file/folder permissions: folders usually `755`, files usually `644`.
- Check the app error log in cPanel.
