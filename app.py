# Campus Sports Hub - Flask + SQLite project
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "change-this-secret"   # needed by Flask to keep the login session safe
STAFF_PASSWORD = "gym123"               # change before demo
DB = "sports.db"
FMT = "%Y-%m-%d %H:%M:%S"               # one time format used everywhere
ISSUE_MINUTES = 60                      # items are issued for 1 hour


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row      # lets us use row["name"] instead of row[0]
    return conn


def now():
    return datetime.now().strftime(FMT)


def init_db():
    """Creates the 3 tables the first time, and adds the gym's equipment."""
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS equipment(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, total INTEGER);
    CREATE TABLE IF NOT EXISTS issues(
        id INTEGER PRIMARY KEY AUTOINCREMENT, equipment_id INTEGER,
        student_name TEXT, roll_no TEXT, issued_at TEXT, due_at TEXT,
        returned_at TEXT);              -- returned_at is empty until item comes back
    CREATE TABLE IF NOT EXISTS crowd_reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT, count INTEGER, reported_at TEXT);
    """)
    if conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0] == 0:
        conn.executemany("INSERT INTO equipment(name,total) VALUES (?,?)", [
            ("Cricket Bat", 1), ("Stumps Set", 1), ("Cricket Ball", 2),
            ("Basketball", 2), ("Football", 2), ("Carrom Board", 3), ("Chess Set", 3)])
    conn.commit()
    conn.close()


def get_equipment():
    """available = total - number of issues that are not yet returned."""
    conn = get_db()
    rows = conn.execute("""
        SELECT e.id, e.name, e.total,
          (SELECT COUNT(*) FROM issues i WHERE i.equipment_id=e.id AND i.returned_at IS NULL) AS issued,
          (SELECT MIN(due_at) FROM issues i WHERE i.equipment_id=e.id AND i.returned_at IS NULL) AS next_due
        FROM equipment e""").fetchall()
    conn.close()
    items = []
    for r in rows:
        d = dict(r)
        d["available"] = d["total"] - d["issued"]
        if d["next_due"]:   # earliest time one will be back
            d["back_by"] = datetime.strptime(d["next_due"], FMT).strftime("%I:%M %p")
        items.append(d)
    return items


@app.route("/")
def home():
    return render_template("index.html", items=get_equipment())


@app.route("/gym", methods=["GET", "POST"])
def gym():
    conn = get_db()
    if request.method == "POST":        # someone submitted a headcount
        count = int(request.form["count"])
        if 0 <= count <= 200:
            conn.execute("INSERT INTO crowd_reports(count, reported_at) VALUES (?,?)", (count, now()))
            conn.commit()
            flash("Thanks! Headcount saved.")
        return redirect(url_for("gym"))

    latest = conn.execute("SELECT * FROM crowd_reports ORDER BY id DESC LIMIT 1").fetchone()
    mins_ago = None
    if latest:
        mins_ago = int((datetime.now() - datetime.strptime(latest["reported_at"], FMT)).total_seconds() // 60)
    # average headcount for every hour of the day (strftime('%H') extracts the hour)
    rows = conn.execute("""SELECT strftime('%H', reported_at) AS hr, AVG(count) AS avg
                           FROM crowd_reports GROUP BY hr ORDER BY hr""").fetchall()
    conn.close()
    biggest = max([r["avg"] for r in rows], default=1) or 1
    hours = [{"label": datetime.strptime(r["hr"], "%H").strftime("%I %p"),
              "avg": round(r["avg"]), "width": int(r["avg"] / biggest * 100)} for r in rows]
    return render_template("gym.html", latest=latest, mins_ago=mins_ago, hours=hours)


@app.route("/staff/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == STAFF_PASSWORD:
            session["staff"] = True     # remember that this browser is logged in
            return redirect(url_for("staff"))
        flash("Wrong password.")
    return render_template("login.html")


@app.route("/staff/logout")
def logout():
    session.pop("staff", None)
    return redirect(url_for("home"))


@app.route("/staff", methods=["GET", "POST"])
def staff():
    if not session.get("staff"):        # only logged-in staff may enter
        return redirect(url_for("login"))
    conn = get_db()
    if request.method == "POST":        # issue an item
        eq_id = int(request.form["equipment_id"])
        item = next(i for i in get_equipment() if i["id"] == eq_id)
        if item["available"] <= 0:
            flash(item["name"] + " is not available.")
        else:
            due = (datetime.now() + timedelta(minutes=ISSUE_MINUTES)).strftime(FMT)
            conn.execute("""INSERT INTO issues(equipment_id, student_name, roll_no, issued_at, due_at)
                            VALUES (?,?,?,?,?)""",
                         (eq_id, request.form["name"], request.form["roll"], now(), due))
            conn.commit()
            flash(item["name"] + " issued.")
        return redirect(url_for("staff"))

    active = conn.execute("""SELECT i.id, e.name AS item, i.student_name, i.roll_no, i.due_at
                             FROM issues i JOIN equipment e ON e.id=i.equipment_id
                             WHERE i.returned_at IS NULL ORDER BY i.due_at""").fetchall()
    conn.close()
    active = [dict(a, overdue=a["due_at"] < now(),
                   due_text=datetime.strptime(a["due_at"], FMT).strftime("%I:%M %p")) for a in active]
    return render_template("staff.html", items=get_equipment(), active=active)


@app.route("/staff/return/<int:issue_id>", methods=["POST"])
def return_item(issue_id):
    if not session.get("staff"):
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("UPDATE issues SET returned_at=? WHERE id=?", (now(), issue_id))
    conn.commit()
    conn.close()
    return redirect(url_for("staff"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
