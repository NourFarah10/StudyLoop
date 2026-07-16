from flask import Flask, render_template, session

app = Flask(__name__)

# Secret key for sessions
app.secret_key = "change_this_to_a_random_secret_key"


# =========================
# Public Routes
# =========================

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/search")
def search():
    return render_template("search.html")


# =========================
# Authentication
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("home.html")


# =========================
# Communities
# =========================

@app.route("/communities")
def communities():
    return "Coming Soon"


@app.route("/community/<int:community_id>")
def community(community_id):
    return render_template(
        "community.html",
        community_id=community_id
    )


@app.route("/request-community", methods=["GET", "POST"])
def request_community():
    return "Coming Soon"


# =========================
# Posts
# =========================

@app.route("/create-post", methods=["GET", "POST"])
def create_post():
    return "Coming Soon"


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    return f"Edit Post {post_id}"


@app.route("/delete-post/<int:post_id>")
def delete_post(post_id):
    return f"Delete Post {post_id}"


# =========================
# Profile
# =========================

@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    return "Coming Soon"


# =========================
# Settings
# =========================

@app.route("/settings", methods=["GET", "POST"])
def settings():
    return render_template("settings.html")


# =========================
# Error Handlers
# =========================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


# =========================
# Run Application
# =========================

if __name__ == "__main__":
    app.run(debug=True)