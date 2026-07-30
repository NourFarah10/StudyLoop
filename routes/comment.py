from flask import (
    Blueprint,
    jsonify,
    request,
    session
)

from helpers import login_required
from database.db import get_db

comment_bp = Blueprint("comment", __name__)


# =====================================================
# GET COMMENTS
# =====================================================

@comment_bp.route("/api/community/<int:community_id>/posts/<int:post_id>/comments")
@login_required
def get_comments(community_id, post_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id,
            c.content,
            c.created_at,
            c.user_id,
            u.username,
            u.profile_image
        FROM comments c
        JOIN users u
            ON u.id = c.user_id
        WHERE c.post_id = ?
        AND c.parent_comment_id IS NULL
        ORDER BY c.created_at ASC
    """, (post_id,))

    parent_comments = cursor.fetchall()

    comments = []

    for parent in parent_comments:

        # ==========================
        # Parent reaction count
        # ==========================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM comment_reactions
            WHERE comment_id = ?
        """, (parent["id"],))

        reaction_count = cursor.fetchone()["total"]

        # ==========================
        # Current user reaction
        # ==========================

        cursor.execute("""
            SELECT reaction
            FROM comment_reactions
            WHERE comment_id = ?
            AND user_id = ?
        """, (
            parent["id"],
            session["user_id"]
        ))

        user_reaction = cursor.fetchone()

        # ==========================
        # Replies
        # ==========================

        cursor.execute("""
            SELECT
                c.id,
                c.content,
                c.created_at,
                c.user_id,
                u.username,
                u.profile_image
            FROM comments c
            JOIN users u
                ON u.id = c.user_id
            WHERE c.parent_comment_id = ?
            ORDER BY c.created_at ASC
        """, (parent["id"],))

        reply_rows = cursor.fetchall()

        replies = []

        for reply in reply_rows:

            # Reply reaction count

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM comment_reactions
                WHERE comment_id = ?
            """, (reply["id"],))

            reply_reaction_count = cursor.fetchone()["total"]

            # Current user's reply reaction

            cursor.execute("""
                SELECT reaction
                FROM comment_reactions
                WHERE comment_id = ?
                AND user_id = ?
            """, (
                reply["id"],
                session["user_id"]
            ))

            reply_user_reaction = cursor.fetchone()

            replies.append({

                "id": reply["id"],
                "post_id": post_id,
                "parent_comment_id": parent["id"],
                "user_id": reply["user_id"],
                "username": reply["username"],
                "profile_image": reply["profile_image"],
                "content": reply["content"],
                "created_at": reply["created_at"],

                "reaction_total": reply_reaction_count,
                "user_reaction":
                    reply_user_reaction["reaction"]
                    if reply_user_reaction else None

            })

        comments.append({

            "id": parent["id"],
            "post_id": post_id,
            "user_id": parent["user_id"],
            "username": parent["username"],
            "profile_image": parent["profile_image"],
            "content": parent["content"],
            "created_at": parent["created_at"],

            "reaction_total": reaction_count,
            "user_reaction":
                user_reaction["reaction"]
                if user_reaction else None,

            "replies": replies

        })

    conn.close()

    return jsonify(comments)

# =====================================================
# ADD COMMENT
# =====================================================
@comment_bp.route(
    "/api/community/<int:community_id>/posts/<int:post_id>/comment",
    methods=["POST"]
)
@login_required
def add_comment(community_id, post_id):

    data = request.get_json()

    if not data:
        return jsonify({"success": False})

    content = data.get("content", "").strip()

    parent_comment_id = data.get("parent_comment_id")

    if not content:
        return jsonify({"success": False})

    conn = get_db()
    cursor = conn.cursor()

    # Make sure the post exists
    cursor.execute("""
        SELECT id
        FROM posts
        WHERE id = ?
        AND community_id = ?
    """, (
        post_id,
        community_id
    ))

    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"success": False})

    # If this is a reply, make sure the parent comment exists
    if parent_comment_id is not None:

        cursor.execute("""
            SELECT id
            FROM comments
            WHERE id = ?
            AND post_id = ?
        """, (
            parent_comment_id,
            post_id
        ))

        if cursor.fetchone() is None:
            conn.close()
            return jsonify({"success": False})

    # Insert comment / reply
    cursor.execute("""
        INSERT INTO comments
        (
            post_id,
            user_id,
            content,
            parent_comment_id
        )
        VALUES (?, ?, ?, ?)
    """, (
        post_id,
        session["user_id"],
        content,
        parent_comment_id
    ))

    conn.commit()

    comment_id = cursor.lastrowid

    cursor.execute("""
        SELECT
            comments.id,
            comments.post_id,
            comments.parent_comment_id,
            comments.content,
            comments.created_at,
            users.id AS user_id,
            users.username,
            users.profile_image
        FROM comments

        JOIN users
            ON users.id = comments.user_id

        WHERE comments.id = ?
    """, (comment_id,))

    comment = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM comments
        WHERE post_id = ?
    """, (post_id,))

    count = cursor.fetchone()["total"]

    conn.close()

    return jsonify({
        "success": True,
        "count": count,
        "comment": {
            "id": comment["id"],
            "post_id": comment["post_id"],
            "parent_comment_id": comment["parent_comment_id"],
            "user_id": comment["user_id"],
            "username": comment["username"],
            "profile_image": comment["profile_image"],
            "content": comment["content"],
            "created_at": comment["created_at"]
        }
    })


# =====================================================
# EDIT COMMENT
# =====================================================

@comment_bp.route("/api/comments/<int:comment_id>/edit", methods=["POST"])
@login_required
def edit_comment_api(comment_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False
        })

    content = data.get("content", "").strip()

    if not content:
        return jsonify({
            "success": False
        })

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM comments
        WHERE id = ?
    """, (comment_id,))

    comment = cursor.fetchone()

    if not comment:
        conn.close()
        return jsonify({
            "success": False
        })

    if comment["user_id"] != session["user_id"]:
        conn.close()
        return jsonify({
            "success": False
        })

    cursor.execute("""
        UPDATE comments
        SET content = ?
        WHERE id = ?
    """, (
        content,
        comment_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "content": content
    })


# =====================================================
# DELETE COMMENT
# =====================================================

@comment_bp.route("/api/comments/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment_api(comment_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM comments
        WHERE id = ?
    """, (comment_id,))

    comment = cursor.fetchone()

    if not comment:
        conn.close()
        return jsonify({
            "success": False
        })

    if comment["user_id"] != session["user_id"]:
        conn.close()
        return jsonify({
            "success": False
        })

    post_id = comment["post_id"]

    # Delete any replies to this comment first, so they don't
    # get left behind as orphans that still count toward the total
    cursor.execute("""
        DELETE
        FROM comments
        WHERE parent_comment_id = ?
    """, (comment_id,))

    cursor.execute("""
        DELETE
        FROM comments
        WHERE id = ?
    """, (comment_id,))

    conn.commit()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM comments
        WHERE post_id = ?
    """, (post_id,))

    count = cursor.fetchone()["total"]

    conn.close()

    return jsonify({
        "success": True,
        "count": count
    })
# =====================================================
# COMMENT REACTION
# =====================================================

@comment_bp.route("/api/comments/<int:comment_id>/reaction", methods=["POST"])
@login_required
def react_comment(comment_id):

    data = request.get_json()

    reaction = data.get("reaction", "LIKE")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reaction
        FROM comment_reactions
        WHERE comment_id = ?
        AND user_id = ?
    """, (
        comment_id,
        session["user_id"]
    ))

    existing = cursor.fetchone()

    removed = False
    my_reaction = reaction

    # ==========================
    # Remove same reaction
    # ==========================

    if existing and existing["reaction"] == reaction:

        cursor.execute("""
            DELETE
            FROM comment_reactions
            WHERE comment_id = ?
            AND user_id = ?
        """, (
            comment_id,
            session["user_id"]
        ))

        removed = True
        my_reaction = None

    # ==========================
    # Change reaction
    # ==========================

    elif existing:

        cursor.execute("""
            UPDATE comment_reactions
            SET reaction = ?,
                created_at = CURRENT_TIMESTAMP
            WHERE comment_id = ?
            AND user_id = ?
        """, (
            reaction,
            comment_id,
            session["user_id"]
        ))

    # ==========================
    # First reaction
    # ==========================

    else:

        cursor.execute("""
            INSERT INTO comment_reactions
            (
                comment_id,
                user_id,
                reaction
            )
            VALUES (?, ?, ?)
        """, (
            comment_id,
            session["user_id"],
            reaction
        ))

    conn.commit()

    # ==========================
    # Count reactions
    # ==========================

    cursor.execute("""
        SELECT
            reaction,
            COUNT(*) total
        FROM comment_reactions
        WHERE comment_id = ?
        GROUP BY reaction
    """, (comment_id,))

    counts = {}
    total = 0

    for row in cursor.fetchall():

        counts[row["reaction"]] = row["total"]
        total += row["total"]

    conn.close()

    icons = {
        "LIKE": "👍",
        "LOVE": "❤️",
        "CARE": "🥰",
        "HAHA": "😄",
        "WOW": "😮",
        "SAD": "😢",
        "ANGRY": "😡"
    }

    texts = {
        "LIKE": "Like",
        "LOVE": "Love",
        "CARE": "Care",
        "HAHA": "Haha",
        "WOW": "Wow",
        "SAD": "Sad",
        "ANGRY": "Angry"
    }

    if my_reaction:

        icon = icons[my_reaction]
        text = texts[my_reaction]

    else:

        icon = "👍"
        text = "Like"

    return jsonify({

        "success": True,
        "removed": removed,
        "reaction": my_reaction,
        "icon": icon,
        "text": text,
        "reaction_counts": counts,
        "reaction_total": total

    })
@comment_bp.route("/api/comments/<int:comment_id>/reactions")
@login_required
def comment_reactions(comment_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            users.username,
            users.profile_image,
            comment_reactions.reaction

        FROM comment_reactions

        JOIN users
            ON users.id = comment_reactions.user_id

        WHERE comment_reactions.comment_id = ?

        ORDER BY comment_reactions.created_at
    """, (comment_id,))

    reactions = cursor.fetchall()

    conn.close()

    return jsonify(reactions)