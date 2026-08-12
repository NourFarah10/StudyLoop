from flask import Flask, render_template
import sqlite3
import secrets
import os

# Blueprints
from routes.profile import profile_bp
from routes.auth import auth_bp
from routes.comment import comment_bp
from routes.community import community_bp
from routes.home import home_bp
from routes.like import like_bp
from routes.post import post_bp
from routes.settings import settings_bp

from flask import jsonify, request, session
from helpers import login_required, send_reset_email
from database.db import get_db
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

# ==================================
# Mail Configuration
# ==================================

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")

app.config["MAIL_DEFAULT_SENDER"] = (
    "StudyLoop",
    app.config["MAIL_USERNAME"]
)

# ==================================
# Config
# ==================================

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.secret_key = os.environ.get(
    "SECRET_KEY",
    secrets.token_hex(32)
)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

app.mail = mail
app.serializer = serializer

# ==================================
# Register Blueprints
# ==================================

app.register_blueprint(profile_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(home_bp)
app.register_blueprint(like_bp)
app.register_blueprint(community_bp)
app.register_blueprint(post_bp)
app.register_blueprint(settings_bp)


# ==================================
# Public Routes
# ==================================

@app.context_processor
def inject_current_user():

    if "user_id" not in session:
        return {"current_user": None}

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    current_user = cursor.fetchone()

    conn.close()

    return {"current_user": current_user}

@app.route("/")
def landing():
    return render_template("landing/landing.html")

# ==================================
# Error Handlers
# ==================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("errors/500.html"), 500
# ==================================
# Run
# ==================================

if __name__ == "__main__":
    app.run(debug=True)