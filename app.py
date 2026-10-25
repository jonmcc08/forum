from flask import Flask, session, render_template, request, url_for, redirect
import mysql.connector, os, bcrypt
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")
s = bcrypt.gensalt()

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="foruminloggning"
)
mycursor = mydb.cursor()
print(f"Logged into {mydb.database}.")

def userLogin(username, password):
    sql = "SELECT * FROM users WHERE username=%s LIMIT 1;"
    mycursor.execute(sql, (username,))

    user = mycursor.fetchone()
    if user == None:
        return 1 
    hashed_password = password.encode("utf-8")
    encoded_password = user[4].encode("utf-8")
    print(hashed_password)
    print(encoded_password)
    if bcrypt.checkpw(hashed_password, encoded_password):
        return 3
    return 2

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
    if session.get("user") != None:
        return redirect("/")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = userLogin(username, password)

        if user == 1:
            return "Account doesn't exist, please signup here: <a href=/signup>Sign up</a>"
        elif user == 2:
            return "Incorrect password. Please try again", {"Refresh": "2; url=/login"}
        elif user == 3:
            session["user"] = username
            return redirect(url_for("posts"))
        return "Wrong username or password", {"Refresh": "2; url=/login"}
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def account_creation():
    if session.get("user") != None:
        return redirect("/")
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        username = request.form["username"]
        sql = "SELECT * FROM users WHERE username=%s LIMIT 1;"
        mycursor.execute(sql, (username,))
        
        if mycursor.fetchone() != None:
            return "Username is already taken, please try with another username.", {"Refresh": "2; url=/signup"}


        password = request.form["password"].encode("utf-8")
        hashed_pw = bcrypt.hashpw(password, s)
        image = request.files["picture"]
        image_url = "nU.webp"
        if image.filename != "":
            with Image.open(image) as img:
                print(f"Image: {img.size}")
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")

                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                image_url = f"{username}.webp"
                file_upload = os.path.join("static/profile_pictures", image_url)
                img.save(file_upload, "WEBP", quality=80)

        sql = "INSERT INTO users (username, firstname, lastname, email, imageURL, password) VALUES (%s, %s, %s, %s, %s, %s);"
        val = (username, firstname, lastname, email, image_url, hashed_pw)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "added.")
        return "Account created.", {"Refresh": "2; url=/login"}

    return render_template("create-account.html")

@app.route("/signout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/posts")
def posts():
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser
    sql = "SELECT * FROM posts"
    mycursor.execute(sql)
    return render_template("posts.html", posts=mycursor.fetchall())

@app.route("/post/<post>", methods=["GET", "POST"])
def post_loader(post):
    if post == None:
        return "Invalid post URL"

    sql = "SELECT * FROM posts WHERE postname=%s LIMIT 1;"
    mycursor.execute(sql, (post,))
    currentpost = mycursor.fetchone()
    print(currentpost)

    sql = "SELECT * FROM comments WHERE post_id=%s LIMIT 1;"
    mycursor.execute(sql, (currentpost[0],))
    comments = mycursor.fetchall()

    if request.method == "POST":
        return render_template("post.html", sent=True, post=currentpost, comments=comments)
    return render_template("post.html", sent=False, post=currentpost, comments=comments)

@app.route("/create-post", methods=["GET", "POST"])
def createPost():
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser
    if request.method == "POST":
        postname = request.form["postname"]
        sql = "SELECT * FROM posts WHERE postname=%s LIMIT 1;"
        mycursor.execute(sql, (postname,))
        if mycursor.fetchone() != None:
            return render_template("create-post.html", alreadyPost=True)

        postdescription = request.form["postmessage"]

        sql = "INSERT INTO posts (user, postname, postdescription, uploadtime) VALUES (%s, %s, %s, NOW())"
        val = (session.get("user"), postname, postdescription)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "added.")
        return "Created Post"
    return render_template("create-post.html")

app.run(host="0.0.0.0", port=5000, debug=True)