# NSUT Sports Hub — deployment

Upload the contents of this folder to a GitHub repository. On Render create a Python Web Service with build command `pip install -r requirements.txt` and start command `gunicorn --workers 1 --bind 0.0.0.0:$PORT app:app`. Set SECRET_KEY to a random secret and STAFF_PASSWORD to a strong private password in Environment. Do not commit secrets.

The database is created automatically with sample equipment. Free Render storage is ephemeral: records may be lost on restart or redeploy. For durable SQLite storage use a paid persistent disk mounted at /var/data and set DATABASE_PATH=/var/data/sports.db. For real student use, obtain authorization and add abuse protection, stronger staff authentication and a privacy policy. Public gym reports are unverified.

Local: install requirements, export STAFF_PASSWORD and SECRET_KEY, then python3 app.py.
