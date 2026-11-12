# Campus Sports Hub

## Run
    pip install flask
    python app.py
Open http://127.0.0.1:5000  (staff password: gym123, set in app.py)
Other phones on the same WiFi: use app.run(host="0.0.0.0") and your laptop's IP.

## Files
- app.py: all Python logic (routes + database)
- templates/: HTML pages (Jinja fills in data)
- static/style.css: looks
- sports.db: created automatically on first run

## Viva Q&A
**Why Flask?** Small Python web framework; maps URLs to Python functions.
**What is a route?** `@app.route("/gym")` links a URL to a function.
**Why SQLite?** Built into Python, one file, no setup.
**3 tables?** equipment (items+quantity), issues (who took what, when, due, returned), crowd_reports (headcount+time).
**How is availability computed?** total minus issues where returned_at is empty.
**How does return work?** Sets returned_at, so the item stops counting as issued.
**What does Jinja do?** `{{ }}` prints values, `{% for %}` loops, in HTML templates.
**GET vs POST?** GET loads a page; POST sends form data.
**How does the hourly chart work?** SQL groups reports by hour (`strftime('%H')`) and takes AVG.
**How is staff login done?** Password check, then `session["staff"]=True` marks the browser logged in.
**Why `?` in SQL?** Placeholders stop SQL injection.
**Limitations / future work?** Single shared password, no student login, no email reminders.
