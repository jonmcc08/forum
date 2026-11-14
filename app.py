# Vad som behövs för detta projekt:
# ---------------------------------
# Flask: pip install flask
# MySQL: pip install mysql
# bCrypt: pip install bcrypt
# Pillow: pip install pillow
# Dotenv: pip install dotenv

# OBS!!! Eftersom att jag döpte "threads" till "posts" förut kommer backend fortfarande behålla post, men tänk det som en thread.

# För att skapa allt som behövs för programmet inom XAMPP så behövs en databas som heter "foruminloggning" skapas och sedan kopiera nedanstående SQL:
# CREATE TABLE users (id INT(11) AUTO_INCREMENT, username VARCHAR(55), firstname VARCHAR(55), lastname VARCHAR(55), password VARCHAR(255), email VARCHAR(50), imageURL VARCHAR(60), PRIMARY KEY (id));
# CREATE TABLE posts (postid INT(11) AUTO_INCREMENT, user VARCHAR(55), postname VARCHAR(50), postdescription VARCHAR(500), uploadtime DATETIME, lastcommenttime DATETIME DEFAULT NULL, PRIMARY KEY (postid));
# CREATE TABLE comments (id INT(11) AUTO_INCREMENT, post_id INT(11), comment_user VARCHAR(50), comment VARCHAR(500), uploadtime DATETIME, PRIMARY KEY (id));

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
    if bcrypt.checkpw(hashed_password, encoded_password):
        return 3
    return 2

def loggedIn():
    user = session.get("user")
    if not user:
        return render_template("reject-login.html"), {"Refresh": "3; url=/login"}
    return None

def saveImage(image, filename):
    image_url = "nU.webp"
    if image.filename != "":
        with Image.open(image) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            image_url = f"{filename}.webp"
            file_upload = os.path.join("static/profile_pictures", image_url)
            img.save(file_upload, "WEBP", quality=80)
    return image_url

def editUserPage(username):
    sql = "SELECT id, imageURL FROM users WHERE username=%s LIMIT 1;"
    mycursor.execute(sql, (username,))
    user = mycursor.fetchone()
    id = user[0]
    imageURL = user[1]
    oldpassword = request.form["oldpassword"]
    user_login = userLogin(username, oldpassword)
    if user_login != 3:
        return False
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    email = request.form["email"]
    name = request.form["username"]
    password = request.form["password"].encode("utf-8")
    image = request.files["picture"]

    sqlfield = []
    sqlVars = []
    if name:
        sql = "SELECT * FROM users WHERE username=%s LIMIT 1;"
        mycursor.execute(sql, (name,))
        if mycursor.fetchone():
            return 2
        sqlfield.append("username = %s")
        sqlVars.append(name)
        changeName(name, username)

        if not image and (imageURL != "nU.webp"):
            oldfile = os.path.join(app.static_folder, "profile_pictures", f"{username}.webp")
            newfile = os.path.join(app.static_folder, "profile_pictures", f"{name}.webp")
            os.rename(oldfile, newfile)

            sqlfield.append("imageURL = %s")
            sqlVars.append(f"{name}.webp")
    if image:
        sqlfield.append("imageURL = %s")
        newusername = username
        if name:
            newusername = name
        saveImage(image, newusername)
        sqlVars.append(f"{newusername}.webp")
    if firstname:
        sqlfield.append("firstname = %s")
        sqlVars.append(firstname)
    if lastname:
        sqlfield.append("lastname = %s")
        sqlVars.append(lastname)
    if email:
        sqlfield.append("email = %s")
        sqlVars.append(email)
    if password:
        hashed_pw = bcrypt.hashpw(password, s)
        sqlfield.append("password = %s")
        sqlVars.append(hashed_pw)

    if sqlfield:
        sql = "UPDATE users SET " + " ,".join(sqlfield) + " WHERE id=%s"
        sqlVars.append(id)

        mycursor.execute(sql, tuple(sqlVars))
        mydb.commit()
        return True
    return 1 # Error message for user.

def changeName(newName, oldName):
    sql = "UPDATE posts SET user=%s WHERE user=%s;"
    mycursor.execute(sql, (newName, oldName,))
    sql = "UPDATE comments SET comment_user=%s WHERE comment_user=%s;"
    mycursor.execute(sql, (newName, oldName,))
    mydb.commit()

    session.clear()
    session["user"] = newName

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

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
            return "Account doesn't exist, please signup here: <a href=/signup>Sign up</a>", {"Refresh": "3; url=/login"}
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
        image_url = saveImage(image, username)

        sql = "INSERT INTO users (username, firstname, lastname, email, imageURL, password) VALUES (%s, %s, %s, %s, %s, %s);"
        val = (username, firstname, lastname, email, image_url, hashed_pw)
        mycursor.execute(sql, val)
        mydb.commit()
        return "Account created.", {"Refresh": "2; url=/login"}

    return render_template("create-account.html")

@app.route("/signout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/threads")
def posts():
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser
    sql = "SELECT posts.*, users.imageURL FROM posts LEFT JOIN users ON posts.user = users.username"
    mycursor.execute(sql)
    return render_template("posts.html", threads=mycursor.fetchall())

@app.route("/thread/<thread>", methods=["GET", "POST"])
def thread_loader(thread):
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser
    sql = "SELECT posts.*, users.imageURL FROM posts LEFT JOIN users ON posts.user = users.username WHERE posts.postname = %s"
    mycursor.execute(sql, (thread,))
    currentpost = mycursor.fetchone()
    if currentpost == None:
        return "Invalid thread", {"Refresh": "3; url=/threads"}

    if request.method == "POST":
        sql = "INSERT INTO comments (post_id, comment_user, comment, uploadtime) VALUES (%s, %s, %s, NOW())"
        user = session.get("user")
        comment = request.form["commentPost"]
        val = (currentpost[0], user, comment)
        mycursor.execute(sql, val)
        mydb.commit()
        # Uppdaterar timern på post pagen
        sql = "UPDATE posts SET lastcommenttime = NOW() WHERE postname = %s"
        mycursor.execute(sql, (thread,))
        mydb.commit()
        
    sql = "SELECT comments.*, users.imageURL FROM comments LEFT JOIN users ON comments.comment_user = users.username WHERE post_id=%s"
    mycursor.execute(sql, (currentpost[0],))
    comments = mycursor.fetchall()

    if request.method == "POST":
        return render_template("post.html", sent=True, post=currentpost, comments=comments)
    return render_template("post.html", sent=False, post=currentpost, comments=comments)

@app.route("/user/<user>")
def user_loader(user):
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser

    sql = "SELECT * FROM users WHERE username=%s LIMIT 1;"
    mycursor.execute(sql, (user,))
    currentuser = mycursor.fetchone()

    if currentuser == None:
        return "Invalid user", {"Refresh": "3; url=/threads"}
    sql = "SELECT DISTINCT posts.* FROM posts JOIN comments ON posts.postid = comments.post_id WHERE posts.user = %s OR comments.comment_user = %s;"
    mycursor.execute(sql, (currentuser[1], currentuser[1]))
    activities = mycursor.fetchall()

    sql = "SELECT * FROM comments WHERE comment_user=%s;"
    mycursor.execute(sql, (user,))
    comments = mycursor.fetchall()
    return render_template("user.html", user=currentuser, currentAccount=(user==session.get("user")), activity=activities, comments=comments)

@app.route("/edit-user", methods=["GET", "POST"])
def editUser():
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser
    
    editedPage = None

    if request.method == "POST":
        username = session.get("user")
        editedPage = editUserPage(username)

    username = session.get("user")
    sql = "SELECT * FROM users WHERE username=%s LIMIT 1;"
    mycursor.execute(sql, (username,))
    user = mycursor.fetchone()
    return render_template("edit-user.html", user=user, editedPage=editedPage)

@app.route("/create-thread", methods=["GET", "POST"])
def createPost():
    loggedInUser = loggedIn()
    if loggedInUser:
        return loggedInUser
    if request.method == "POST":
        postname = request.form["postname"]
        sql = "SELECT * FROM posts WHERE postname=%s LIMIT 1;"
        mycursor.execute(sql, (postname,))
        if mycursor.fetchone() != None:
            return render_template("create-thread.html", alreadyPost=True)

        postdescription = request.form["postmessage"]

        sql = "INSERT INTO posts (user, postname, postdescription, uploadtime) VALUES (%s, %s, %s, NOW())"
        val = (session.get("user"), postname, postdescription)
        mycursor.execute(sql, val)
        mydb.commit()
        return "Created Thread", {"Refresh": "3; url=/threads"}
    return render_template("create-thread.html")

app.run(host="0.0.0.0", port=5000, debug=True)