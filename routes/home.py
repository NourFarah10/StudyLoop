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
from datetime import datetime

home_bp = Blueprint("home", __name__)

@home_bp.route("/home")
@login_required
def home():

    conn = get_db()
    cursor = conn.cursor()

    # =========================
    # Current user
    # =========================

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    # =========================
    # Communities the user joined
    # =========================

    cursor.execute("""
        SELECT
            communities.*,
            (
                SELECT COUNT(*)
                FROM community_members
                WHERE community_id = communities.id
            ) AS member_count

        FROM communities

        JOIN community_members
            ON communities.id = community_members.community_id

        WHERE community_members.user_id = ?

        ORDER BY communities.name
    """, (session["user_id"],))

    joined_communities = cursor.fetchall()

    # =========================
    # Recommended Communities
    # =========================
    # Get communities with the most members.
    # Exclude communities the current user already joined.

    cursor.execute("""
        SELECT
            communities.*,
            COUNT(community_members.user_id) AS member_count

        FROM communities

        LEFT JOIN community_members
            ON communities.id = community_members.community_id

        WHERE communities.id NOT IN (
            SELECT community_id
            FROM community_members
            WHERE user_id = ?
        )

        GROUP BY communities.id

        ORDER BY member_count DESC, communities.name ASC

        LIMIT 6
    """, (session["user_id"],))

    recommended_communities = cursor.fetchall()

    conn.close()

    return render_template(
        "home/home.html",
        user=user,
        joined_communities=joined_communities,
        recent_posts=[],
        recommended_communities=recommended_communities
    )