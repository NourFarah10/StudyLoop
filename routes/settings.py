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

from helpers import login_required
from database.db import get_db

settings_bp = Blueprint("settings", __name__)

# =========================
# Settings
# =========================

@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    conn = get_db()
    cursor = conn.cursor()

    # check if user exists
    cursor.execute(
        """
        SELECT * FROM users WHERE id = ?
        """,
        (session["user_id"],)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        flash("User not found")
        return redirect(url_for("auth.signup"))

    if request.method == "GET":
        conn.close()
        return render_template("settings/settings.html", user=user)

    theme = request.form.get("theme")

    email_notifications = (
        1 if request.form.get("email_notifications") else 0
    )

    private_profile = (
        1 if request.form.get("private_profile") else 0
    )

    cursor.execute(
        """
        UPDATE users
        SET
            theme = ?,
            email_notifications = ?,
            private_profile = ?
        WHERE id = ?
        """,
        (
            theme,
            email_notifications,
            private_profile,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash("Settings updated successfully.")

    return redirect(url_for("settings.settings"))