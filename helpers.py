import requests

from flask import redirect, render_template, session, current_app, url_for
from functools import wraps
from flask_mail import Message


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif"
}

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# reset password email function
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def send_reset_email(mail, user_email, reset_link):

    msg = Message(
        "StudyLoop Password Reset",
        recipients=[user_email]
    )

    msg.body = f"""
Hello!

You requested to reset your StudyLoop password.

Click the link below to reset it:

{reset_link}

This link expires in 30 minutes.

If you didn't request this, simply ignore this email.

StudyLoop Team
"""

    mail.send(msg)