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

like_bp = Blueprint("like", __name__)

# =====================================================
# POST REACTION
# =====================================================

@like_bp.route(
    "/api/community/<int:community_id>/posts/<int:post_id>/like",
    methods=["POST"]
)
@login_required
def react_post(community_id, post_id):

    data = request.get_json()

    reaction = data.get("reaction", "LIKE")

    conn = get_db()
    cursor = conn.cursor()

    # ------------------------------------------
    # Existing reaction?
    # ------------------------------------------

    cursor.execute("""
        SELECT reaction
        FROM post_reactions
        WHERE user_id = ?
        AND post_id = ?
    """, (
        session["user_id"],
        post_id
    ))

    existing = cursor.fetchone()
    removed = False
    my_reaction = reaction

    # ------------------------------------------
    # Same reaction -> Remove it
    # ------------------------------------------

    if existing and existing["reaction"] == reaction:

        cursor.execute("""
            DELETE
            FROM post_reactions
            WHERE user_id = ?
            AND post_id = ?
        """, (
            session["user_id"],
            post_id
        ))

        my_reaction = None
        removed = True

    # ------------------------------------------
    # Different reaction -> Update
    # ------------------------------------------

    elif existing:

        cursor.execute("""
            UPDATE post_reactions
            SET reaction = ?,
                created_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            AND post_id = ?
        """, (
            reaction,
            session["user_id"],
            post_id
        ))

    # ------------------------------------------
    # No reaction -> Insert
    # ------------------------------------------

    else:

        cursor.execute("""
            INSERT INTO post_reactions
            (
                user_id,
                post_id,
                reaction
            )
            VALUES (?, ?, ?)
        """, (
            session["user_id"],
            post_id,
            reaction
        ))

    conn.commit()

    # ------------------------------------------
    # Count reactions
    # ------------------------------------------

    cursor.execute("""
        SELECT
            reaction,
            COUNT(*) AS total
        FROM post_reactions
        WHERE post_id = ?
        GROUP BY reaction
    """, (post_id,))

    reaction_counts = {}

    total = 0

    for row in cursor.fetchall():

        reaction_counts[row["reaction"]] = row["total"]

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
        "reaction_counts": reaction_counts,
        "reaction_total": total
    })
# =====================================================
# GET POST REACTIONS
# =====================================================

@like_bp.route(
    "/api/posts/<int:post_id>/reactions"
)
@login_required
def get_post_reactions(post_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            users.username,
            users.profile_image,
            post_reactions.reaction

        FROM post_reactions

        JOIN users
            ON users.id = post_reactions.user_id

        WHERE post_reactions.post_id = ?

        ORDER BY post_reactions.created_at DESC
    """, (post_id,))

    reactions = []

    for row in cursor.fetchall():

        reactions.append({

            "username": row["username"],
            "profile_image": row["profile_image"],
            "reaction": row["reaction"]

        })

    conn.close()

    return jsonify(reactions)