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

import os
import uuid
from werkzeug.utils import secure_filename
from helpers import login_required
from database.db import get_db

community_bp = Blueprint("community", __name__)

# ==========================================================
# SEARCH PAGE
# ==========================================================

@community_bp.route("/community/search")
@login_required
def search_community():
    return render_template("community/community_search.html")


# ==========================================================
# SEARCH API
# ==========================================================

@community_bp.route("/api/community/search")
@login_required
def community_search_api():

    query = request.args.get("q", "").strip()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id,
            c.name,
            c.description,
            c.category,

            COUNT(cm.user_id) AS members,

            EXISTS(
                SELECT 1
                FROM community_members
                WHERE community_id = c.id
                AND user_id = ?
            ) AS joined

        FROM communities c

        LEFT JOIN community_members cm
            ON cm.community_id = c.id

        WHERE c.name LIKE ?

        GROUP BY c.id

        ORDER BY c.name
    """, (
        session["user_id"],
        f"%{query}%"
    ))

    communities = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify(communities)


# ==========================================================
# MY COMMUNITIES
# ==========================================================

@community_bp.route("/communities")
@login_required
def communities():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT communities.*

        FROM communities

        JOIN community_members
            ON community_members.community_id = communities.id

        WHERE community_members.user_id = ?

        ORDER BY communities.name
    """, (session["user_id"],))

    communities = cursor.fetchall()

    conn.close()

    return render_template(
        "community/communities.html",
        communities=communities
    )


# ==========================================================
# COMMUNITY PAGE
# ==========================================================

@community_bp.route("/community/<int:community_id>")
@login_required
def community(community_id):

    conn = get_db()
    cursor = conn.cursor()

    # --------------------------
    # Community
    # --------------------------

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

    # --------------------------
    # Member count
    # --------------------------

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM community_members
        WHERE community_id = ?
    """, (community_id,))

    member_count = cursor.fetchone()["total"]

    # --------------------------
    # Is current user a member?
    # --------------------------

    cursor.execute("""
        SELECT 1
        FROM community_members
        WHERE community_id = ?
        AND user_id = ?
    """, (
        community_id,
        session["user_id"]
    ))

    is_member = cursor.fetchone() is not None
    is_owner = community["created_by"] == session["user_id"]

    # --------------------------
    # Current user
    # --------------------------

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    current_user = cursor.fetchone()

    # --------------------------
    # Posts
    # --------------------------
    cursor.execute("""
        SELECT

            posts.*,

            users.username,
            users.profile_image,
            (
                SELECT COUNT(*)
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
            ) AS reaction_total,

            (
                SELECT COUNT(*)
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
                AND reaction='LIKE'
            ) AS like_count,

            (
                SELECT COUNT(*)
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
                AND reaction='LOVE'
            ) AS love_count,

            (
                SELECT COUNT(*)
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
                AND reaction='CARE'
            ) AS care_count,

            (
                SELECT COUNT(*)
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
                AND reaction='HAHA'
            ) AS haha_count,

            (
                SELECT COUNT(*)
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
                AND reaction='WOW'
            ) AS wow_count,

            (
                SELECT COUNT(*)
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
                AND reaction='SAD'
            ) AS sad_count,

            (
                SELECT COUNT(*)
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
                AND reaction='ANGRY'
            ) AS angry_count,

            (
                SELECT COUNT(*)
                FROM comments
                WHERE comments.post_id = posts.id
            ) AS comment_count,

            (
                SELECT reaction
                FROM post_reactions
                WHERE post_reactions.post_id = posts.id
                AND post_reactions.user_id = ?
                LIMIT 1
            ) AS user_reaction

        FROM posts

        JOIN users
            ON users.id = posts.user_id

        WHERE posts.community_id = ?

        ORDER BY posts.created_at DESC
    """, (
        session["user_id"],
        community_id
    ))

    posts = cursor.fetchall()

    conn.close()

    return render_template(
        "community/community.html",
        community=community,
        member_count=member_count,
        is_member=is_member,
        is_owner=is_owner,
        current_user=current_user,
        posts=posts
    )


# ==========================================================
# CREATE COMMUNITY
# ==========================================================

@community_bp.route("/create-community", methods=["GET", "POST"])
@login_required
def create_community():

    if request.method == "GET":
        return render_template("community/create_community.html")

    community_name = request.form.get("community_name", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category")

    if not community_name:
        flash("Community name is required.")
        return redirect(url_for("community.create_community"))

    if not description:
        flash("Description is required.")
        return redirect(url_for("community.create_community"))

    if not category:
        flash("Category is required.")
        return redirect(url_for("community.create_community"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM communities
        WHERE name = ?
    """, (community_name,))

    if cursor.fetchone():

        conn.close()

        flash("A community with this name already exists.")

        return redirect(url_for("community.create_community"))

    cursor.execute("""
        INSERT INTO communities
        (
            name,
            description,
            cover_image,
            category,
            created_by
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        community_name,
        description,
        None,
        category,
        session["user_id"]
    ))

    community_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO community_members
        (
            user_id,
            community_id
        )
        VALUES (?, ?)
    """, (
        session["user_id"],
        community_id
    ))

    conn.commit()
    conn.close()

    flash("Community created successfully.")

    return redirect(
        url_for(
            "community.community",
            community_id=community_id
        )
    )

# ==========================================================
# EDIT COMMUNITY
# ==========================================================

# ==========================================================
# EDIT COMMUNITY
# ==========================================================

@community_bp.route("/edit-community/<int:community_id>", methods=["GET", "POST"])
@login_required
def edit_community(community_id):

    conn = get_db()
    cursor = conn.cursor()

    # Get community
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

    # Only creator can edit
    if community["created_by"] != session["user_id"]:
        conn.close()
        flash("You don't have permission to edit this community.")
        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    # =====================================================
    # SAVE CHANGES
    # =====================================================

    if request.method == "POST":

        community_name = request.form.get("community_name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category")
        cover_image = request.files.get("cover_image")
        # Validation
        if not community_name:
            flash("Community name is required.")
            conn.close()
            return redirect(request.url)

        if not description:
            flash("Description is required.")
            conn.close()
            return redirect(request.url)

        if not category:
            flash("Category is required.")
            conn.close()
            return redirect(request.url)

        # Check duplicate name
        cursor.execute("""
            SELECT id
            FROM communities
            WHERE name = ?
            AND id != ?
        """, (
            community_name,
            community_id
        ))

        if cursor.fetchone():
            conn.close()
            flash("Another community already has this name.")
            return redirect(request.url)

        # Keep the current image unless a new one is uploaded
        filename = community["cover_image"]

        if cover_image and cover_image.filename:

            extension = os.path.splitext(cover_image.filename)[1].lower()

            filename = f"{uuid.uuid4().hex}{extension}"

            upload_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename
            )

            cover_image.save(upload_path)

            # Delete old image if it exists
            if community["cover_image"]:

                old_image = os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    community["cover_image"]
                )

                if os.path.exists(old_image):
                    os.remove(old_image)

        # Update community
        cursor.execute("""
            UPDATE communities
            SET
                name = ?,
                description = ?,
                category = ?,
                cover_image = ?
            WHERE id = ?
        """, (
            community_name,
            description,
            category,
            filename,
            community_id
        ))

        conn.commit()
        conn.close()

        flash("Community updated successfully!")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    # =====================================================
    # SHOW EDIT PAGE
    # =====================================================

    conn.close()

    return render_template(
        "community/edit_community.html",
        community=community
    )

# ==========================================================
# JOIN COMMUNITY
# ==========================================================

@community_bp.route("/join-community/<int:community_id>")
@login_required
def join_community(community_id):

    conn = get_db()
    cursor = conn.cursor()

    # Community exists?
    cursor.execute("""
        SELECT id
        FROM communities
        WHERE id = ?
    """, (community_id,))

    if cursor.fetchone() is None:

        conn.close()

        flash("Community not found.")

        return redirect(url_for("community.communities"))

    # Already a member?
    cursor.execute("""
        SELECT 1
        FROM community_members
        WHERE user_id = ?
        AND community_id = ?
    """, (
        session["user_id"],
        community_id
    ))

    if cursor.fetchone():

        conn.close()

        flash("You are already a member.")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    # Join community
    cursor.execute("""
        INSERT INTO community_members
        (
            user_id,
            community_id
        )
        VALUES (?, ?)
    """, (
        session["user_id"],
        community_id
    ))

    conn.commit()
    conn.close()

    flash("You joined the community!")

    return redirect(
        url_for(
            "community.community",
            community_id=community_id
        )
    )


# ==========================================================
# LEAVE COMMUNITY
# ==========================================================

@community_bp.route("/leave-community/<int:community_id>")
@login_required
def leave_community(community_id):

    conn = get_db()
    cursor = conn.cursor()

    # Community exists?
    cursor.execute("""
        SELECT id
        FROM communities
        WHERE id = ?
    """, (community_id,))

    if cursor.fetchone() is None:

        conn.close()

        flash("Community not found.")

        return redirect(url_for("community.communities"))

    # Creator cannot leave
    cursor.execute("""
        SELECT created_by
        FROM communities
        WHERE id = ?
    """, (community_id,))

    community = cursor.fetchone()

    if community["created_by"] == session["user_id"]:

        conn.close()

        flash("The creator cannot leave their own community.")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    # Is member?
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

        flash("You are not a member.")

        return redirect(
            url_for(
                "community.community",
                community_id=community_id
            )
        )

    # Leave
    cursor.execute("""
        DELETE FROM community_members
        WHERE user_id = ?
        AND community_id = ?
    """, (
        session["user_id"],
        community_id
    ))

    conn.commit()
    conn.close()

    flash("You left the community.")

    return redirect(url_for("community.communities"))