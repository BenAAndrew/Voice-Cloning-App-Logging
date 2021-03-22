from flask import Flask, request, render_template, Response
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import threading


app = Flask(__name__, template_folder="static")
service_password = os.getenv("SERVICE_PASSWORD")

# db
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Error(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    stacktrace = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)


@app.route("/", methods=["GET", "POST"])
def log():
    try:
        error = Error(**request.data)
        db.session.add(error)
        db.session.commit()
    except:
        return Response(status=400)

    return Response(status=201)


@app.route("/view", methods=["GET", "POST"])
def view():
    logs = None
    if request.method == "POST":
        if request.values["password"] == service_password:
            logs = Error.query.all()

    return render_template("view.html", logs=logs)

lock = threading.Lock()
with lock:
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
