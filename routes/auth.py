from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    jsonify
)

from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, send_reset_email
from database.db import get_db

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app

auth_bp = Blueprint("auth", __name__)

# =========================
# Authentication
# =========================

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")
    fullname = request.form.get("fullname")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # check for blank inputs
    if not fullname:
        flash("fullname is required")
        return redirect(url_for("auth.signup"))
    if not username:
        flash("username is required")
        return redirect(url_for("auth.signup"))
    if not email:
        flash("email is required")
        return redirect(url_for("auth.signup"))
    if not password:
        flash("password is required")
        return redirect(url_for("auth.signup"))
    if not confirmation:
        flash("password confirmation is required")
        return redirect(url_for("auth.signup"))
    if password != confirmation:
        flash("passwords do not match")
        return redirect(url_for("auth.signup"))   

    # check if username already exists
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    username_exists = cursor.fetchone()
    if username_exists:
        conn.close()
        flash("Username already exists")
        return redirect(url_for("auth.signup"))

    # check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    email_exists = cursor.fetchone()
    if email_exists:
        conn.close()
        flash("Email already exists")
        return redirect(url_for("auth.signup"))

    # hash the password
    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (fullname, username, email, password_hash) VALUES (?, ?, ?, ?)"
        , (fullname, username, email, password_hash))
    conn.commit()

    # store user id in the session
    user_id = cursor.lastrowid
    session["user_id"] = user_id
    conn.close()
    return redirect(url_for("home.home"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("auth/login.html")
    username = request.form.get("username")
    password = request.form.get("password")

    # check for blank inputs
    if not username:
        flash("username is required")
        return redirect(url_for("auth.login"))
    if not password:
        flash("password is required")
        return redirect(url_for("auth.login"))

    conn = get_db()
    cursor = conn.cursor()

    # check if user had an account
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user or not check_password_hash(
        user["password_hash"], password
    ):
        flash("Invalid username and/or password")
        conn.close()
        return redirect(url_for("auth.login"))

    session["user_id"] = user["id"]
    conn.close()
    return redirect(url_for("home.home"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("landing"))

@auth_bp.route("/forget-password", methods=["GET", "POST"])
def forget_password():

    if request.method == "GET":
        return render_template("auth/forget_password.html")

    email = request.form.get("email")

    if not email:
        flash("Email is required.")
        return redirect(url_for("auth.forget_password"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    if user:

        token = current_app.serializer.dumps(
            email,
            salt="password-reset"
        )

        reset_link = url_for(
            "auth.reset_password",
            token=token,
            _external=True
        )

        send_reset_email(
            current_app.mail,
            email,
            reset_link
        )

    conn.close()

    flash(
        "If an account with that email exists, a password reset link has been sent."
    )

    return redirect(url_for("auth.login"))

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    try:
        email = current_app.serializer.loads(
            token,
            salt="password-reset",
            max_age=3600  # 1 hour
        )

    except SignatureExpired:
        flash("This reset link has expired.")
        return redirect(url_for("auth.forget_password"))

    except BadSignature:
        flash("Invalid password reset link.")
        return redirect(url_for("auth.forget_password"))

    if request.method == "GET":
        return render_template(
            "auth/reset_password.html",
            token=token
        )

    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if not password:
        flash("Password is required.")
        return redirect(
            url_for("auth.reset_password", token=token)
        )

    if password != confirmation:
        flash("Passwords do not match.")
        return redirect(
            url_for("auth.reset_password", token=token)
        )

    password_hash = generate_password_hash(password)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET password_hash = ?
        WHERE email = ?
    """, (
        password_hash,
        email
    ))

    conn.commit()
    conn.close()

    flash("Your password has been reset successfully. Please log in.")

    return redirect(url_for("auth.login"))