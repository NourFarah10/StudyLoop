from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for
)

from helpers import login_required
from database.db import get_db

post_bp = Blueprint("post", __name__)


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

        conn.close()

        return render_template(
            "community/edit_post.html",
            post=post,
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