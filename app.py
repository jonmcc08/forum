from flask import Flask, session, render_template, request, url_for, redirect

app = Flask(__name__)
app.secret_key = "1TSJ0NTEYTS3CR3TK3Y"

# Temporärt tills när databaser är lärda
USERS = {
    'admin': {"password": "123"},
    'jonte': {"password": "Twitch.tv/ItsJonteYT"}
}

def loggedIn():
    user = session.get("user")
    if not user:
        return render_template("reject-login.html"), {"Refresh": "3; url=/login"}
    return None

@app.route("/")
def homepage():
    return render_template("main.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = USERS.get(username)
        if user and user["password"] == password:
            session["user"] = username
            return redirect(url_for("posts"))
        return "Wrong username or password", {"Refresh": "2; url=/login"}
    return render_template("login.html")

@app.route("/signup")
def account_creation():
    return render_template("base.html")

@app.route("/posts")
def posts():
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser
    return render_template("posts.html")

@app.route("/create-post", methods=["GET", "POST"])
def createPost():
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser
    if request.method == "POST":
        # Mer kod senare        
        return "Created Post"
    return render_template("create.html")

app.run(host="0.0.0.0", port=5000, debug=True)