from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    current_app
)

import os
import uuid

from helpers import login_required
from database.db import get_db

post_bp = Blueprint("post", __name__)


# ==========================================================
# MEDIA HELPERS
# ==========================================================

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov"}


def save_post_media(files, post_id, cursor):
    """
    Saves each uploaded file to disk and inserts a matching row into
    post_media. Files with an unsupported extension are silently
    skipped. Multiple files (images and/or videos, mixed) are all
    attached to the same post_id.
    """

    for file in files:

        if not file or not file.filename:
            continue

        extension = os.path.splitext(file.filename)[1].lower().lstrip(".")

        if extension in ALLOWED_IMAGE_EXTENSIONS:
            media_type = "image"
        elif extension in ALLOWED_VIDEO_EXTENSIONS:
            media_type = "video"
        else:
            # Unsupported file type — skip it rather than failing
            # the whole post submission.
            continue

        filename = f"{uuid.uuid4().hex}.{extension}"

        upload_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(upload_path)

        cursor.execute("""
            INSERT INTO post_media
            (
                post_id,
                file_path,
                media_type
            )
            VALUES (?, ?, ?)
        """, (
            post_id,
            filename,
            media_type
        ))


def delete_post_media_files(media_rows):
    """
    Deletes the actual files on disk for the given post_media rows.
    (Deleting the DB rows themselves is handled separately — either
    via explicit DELETE, or automatically via ON DELETE CASCADE when
    the parent post is deleted.)
    """

    for media in media_rows:

        file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            media["file_path"]
        )

        if os.path.exists(file_path):
            os.remove(file_path)


# ==========================================================
# CREATE POST
# ==========================================================

@post_bp.route("/community/<int:community_id>/posts/create", methods=["GET", "POST"])
@login_required
def create_post(community_id):

    conn = get_db()
    cursor = conn.cursor()

    # Community exists?
    cursor.execute("""
        SELECT *
        FROM communities
        WHERE id = ?
    """, (community_id,))

    community = cursor.fetchone()

    if community is None:
        conn.close()
        flash("Community not found.")
        return redirect(url_for("community.communities"))

    # User is a member?
    cursor.execute("""
        SELECT 1
        FROM community_members
        WHERE user_id = ?
        AND community_id = ?
    """, (
        session["user_id"],
        community_id
    ))

    if cursor.fetchone() is None:

        conn.close()

        flash("Join the community before creating a post.")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    user = cursor.fetchone()

    if request.method == "GET":

        conn.close()

        return render_template(
            "community/create_post.html",
            community=community,
            community_id=community_id,
            user=user
        )

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    tag = request.form.get("tag")

    if not title:

        conn.close()

        flash("Title is required.")

        return redirect(
            url_for(
                "post.create_post",
                community_id=community_id
            )
        )

    if not content:

        conn.close()

        flash("Content is required.")

        return redirect(
            url_for(
                "post.create_post",
                community_id=community_id
            )
        )

    if not tag:

        conn.close()

        flash("Tag is required.")

        return redirect(
            url_for(
                "post.create_post",
                community_id=community_id
            )
        )

    cursor.execute("""
        INSERT INTO posts
        (
            community_id,
            user_id,
            title,
            content,
            tag
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        community_id,
        session["user_id"],
        title,
        content,
        tag
    ))

    post_id = cursor.lastrowid

    media_files = request.files.getlist("media")
    save_post_media(media_files, post_id, cursor)

    conn.commit()
    conn.close()

    flash("Post created successfully!")

    return redirect(
        url_for(
            "community.community",
            community_id=community_id
        )
    )


# ==========================================================
# EDIT POST
# ==========================================================

@post_bp.route("/community/<int:community_id>/posts/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(community_id, post_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM communities
        WHERE id = ?
    """, (community_id,))

    community = cursor.fetchone()

    if community is None:

        conn.close()

        flash("Community not found.")

        return redirect(url_for("community.communities"))

    cursor.execute("""
        SELECT *
        FROM posts
        WHERE id = ?
        AND community_id = ?
    """, (
        post_id,
        community_id
    ))

    post = cursor.fetchone()

    if post is None:

        conn.close()

        flash("Post not found.")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    if post["user_id"] != session["user_id"]:

        conn.close()

        flash("You can only edit your own posts.")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    user = cursor.fetchone()

    if request.method == "GET":

        cursor.execute("""
            SELECT *
            FROM post_media
            WHERE post_id = ?
            ORDER BY id ASC
        """, (post_id,))

        existing_media = cursor.fetchall()

        conn.close()

        return render_template(
            "community/edit_post.html",
            post=post,
            community_id=community_id,
            user=user,
            existing_media=existing_media
        )

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    tag = request.form.get("tag")

    if not title:

        conn.close()

        flash("Title is required.")

        return redirect(
            url_for(
                "post.edit_post",
                community_id=community_id,
                post_id=post_id
            )
        )

    if not content:

        conn.close()

        flash("Content is required.")

        return redirect(
            url_for(
                "post.edit_post",
                community_id=community_id,
                post_id=post_id
            )
        )

    if not tag:

        conn.close()

        flash("Tag is required.")

        return redirect(
            url_for(
                "post.edit_post",
                community_id=community_id,
                post_id=post_id
            )
        )

    # -----------------------------------------
    # Remove any media the user checked for deletion
    # -----------------------------------------

    delete_media_ids = request.form.getlist("delete_media")

    if delete_media_ids:

        placeholders = ",".join("?" * len(delete_media_ids))

        cursor.execute(f"""
            SELECT id, file_path
            FROM post_media
            WHERE id IN ({placeholders})
            AND post_id = ?
        """, (*delete_media_ids, post_id))

        media_to_delete = cursor.fetchall()

        delete_post_media_files(media_to_delete)

        cursor.execute(f"""
            DELETE FROM post_media
            WHERE id IN ({placeholders})
            AND post_id = ?
        """, (*delete_media_ids, post_id))

    # -----------------------------------------
    # Add any newly uploaded media
    # -----------------------------------------

    new_media_files = request.files.getlist("media")
    save_post_media(new_media_files, post_id, cursor)

    cursor.execute("""
        UPDATE posts

        SET

            title = ?,
            content = ?,
            tag = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE id = ?
    """, (
        title,
        content,
        tag,
        post_id
    ))

    conn.commit()
    conn.close()

    flash("Post updated successfully!")

    return redirect(
        url_for(
            "community.community",
            community_id=community_id
        )
    )


# ==========================================================
# DELETE POST
# ==========================================================

@post_bp.route("/community/<int:community_id>/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(community_id, post_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM posts
        WHERE id = ?
        AND community_id = ?
    """, (
        post_id,
        community_id
    ))

    post = cursor.fetchone()

    if post is None:

        conn.close()

        flash("Post not found.")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    if post["user_id"] != session["user_id"]:

        conn.close()

        flash("You can only delete your own posts.")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    # Delete media files from disk before deleting the post — the
    # post_media rows themselves are removed automatically via
    # ON DELETE CASCADE once the post row is deleted below.
    cursor.execute("""
        SELECT file_path
        FROM post_media
        WHERE post_id = ?
    """, (post_id,))

    media_rows = cursor.fetchall()

    delete_post_media_files(media_rows)

    cursor.execute("""
        DELETE
        FROM posts
        WHERE id = ?
    """, (post_id,))

    conn.commit()
    conn.close()

    flash("Post deleted successfully!")

    return redirect(
        url_for(
            "community.community",
            community_id=community_id
        )
    )