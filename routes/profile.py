from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    jsonify,
    current_app
)

from werkzeug.utils import secure_filename
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import os

from helpers import login_required, allowed_file
from database.db import get_db

profile_bp = Blueprint("profile", __name__)

# =========================
# Profile
# =========================

@profile_bp.route("/profile")
@login_required
def profile():
    conn = get_db()
    cursor = conn.cursor()

    # Current user
    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    )
    user = cursor.fetchone()

    # Number of joined communities
    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM community_members
        WHERE user_id = ?
        """,
        (session["user_id"],)
    )
    community_count = cursor.fetchone()["count"]

    # Number of posts
    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM posts
        WHERE user_id = ?
        """,
        (session["user_id"],)
    )
    post_count = cursor.fetchone()["count"]

    # Number of comments
    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM comments
        WHERE user_id = ?
        """,
        (session["user_id"],)
    )
    comment_count = cursor.fetchone()["count"]

    # Joined communities
    cursor.execute(
        """
        SELECT communities.*
        FROM communities
        JOIN community_members
            ON communities.id = community_members.community_id
        WHERE community_members.user_id = ?
        ORDER BY communities.name
        """,
        (session["user_id"],)
    )
    joined_communities = cursor.fetchall()

    conn.close()

    return render_template(
        "profile/profile.html",
        user=user,
        community_count=community_count,
        post_count=post_count,
        comment_count=comment_count,
        joined_communities=joined_communities
    )


@profile_bp.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    conn = get_db()
    cursor = conn.cursor()

    # Get current user
    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    user = cursor.fetchone()

    if not user:
        conn.close()
        flash("You don't have an account.")
        return redirect(url_for("auth.signup"))

    if request.method == "GET":
        conn.close()
        return render_template(
            "profile/edit_profile.html",
            user=user
        )

    # -----------------------------
    # Form Data
    # -----------------------------

    fullname = request.form.get("fullname")
    username = request.form.get("username")
    email = request.form.get("email")

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirmation = request.form.get("confirmation")

    profile_image = request.files.get("profile_image")

    # Keep old values if blank

    if not fullname:
        fullname = user["fullname"]

    if not username:
        username = user["username"]

    if not email:
        email = user["email"]

    # -----------------------------
    # Username validation
    # -----------------------------

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
        AND id != ?
    """, (username, session["user_id"]))

    if cursor.fetchone():
        conn.close()
        flash("Username already exists.")
        return redirect(url_for("profile.edit_profile"))

    # -----------------------------
    # Email validation
    # -----------------------------

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email = ?
        AND id != ?
    """, (email, session["user_id"]))

    if cursor.fetchone():
        conn.close()
        flash("Email already exists.")
        return redirect(url_for("profile.edit_profile"))

    # -----------------------------
    # Profile Image
    # -----------------------------

    image_filename = user["profile_image"]

    if profile_image and profile_image.filename != "":

        if allowed_file(profile_image.filename):

            filename = secure_filename(profile_image.filename)

            filename = (
                f"user_{session['user_id']}_{filename}"
            )

            save_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename
            )

            profile_image.save(save_path)

            image_filename = filename

        else:
            conn.close()
            flash("Invalid image type.")
            return redirect(url_for("profile.edit_profile"))

    # -----------------------------
    # Password
    # -----------------------------

    password_hash = user["password_hash"]

    if current_password or new_password or confirmation:

        if not current_password:
            conn.close()
            flash("Current password is required.")
            return redirect(url_for("profile.edit_profile"))

        if not new_password:
            conn.close()
            flash("New password is required.")
            return redirect(url_for("profile.edit_profile"))

        if not confirmation:
            conn.close()
            flash("Please confirm your password.")
            return redirect(url_for("profile.edit_profile"))

        if not check_password_hash(
            user["password_hash"],
            current_password
        ):
            conn.close()
            flash("Current password is incorrect.")
            return redirect(url_for("profile.edit_profile"))

        if new_password != confirmation:
            conn.close()
            flash("Passwords do not match.")
            return redirect(url_for("profile.edit_profile"))

        password_hash = generate_password_hash(new_password)

    # -----------------------------
    # Update User
    # -----------------------------

    cursor.execute("""
        UPDATE users
        SET
            fullname = ?,
            username = ?,
            email = ?,
            profile_image = ?,
            password_hash = ?
        WHERE id = ?
    """, (
        fullname,
        username,
        email,
        image_filename,
        password_hash,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    flash("Profile updated successfully!")

    return redirect(url_for("profile.profile"))