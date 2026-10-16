from flask import Flask, session, render_template, request, url_for, redirect
import mysql.connector, os
from fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")
encryption_key = os.getenv("PASSWORD_ENCRYPTION_KEY")
assert encryption_key
FERNET = Fernet(encryption_key) #Fixa

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
    userPswd = user[4]
    if password == userPswd:
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
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = userLogin(username, password)

        if user == 1:
            return "Account doesn't exist, please signup here: <a href=/signup>Signup</a>"
        elif user == 2:
            return "Incorrect password. Please try again", {"Refresh": "2; url=/login"}
        elif user == 3:
            session["user"] = username
            return redirect(url_for("posts"))
        return "Wrong username or password", {"Refresh": "2; url=/login"}
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def account_creation():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        username = request.form["username"]
        sql = "SELECT * FROM users WHERE username=%s LIMIT 1;"
        mycursor.execute(sql, (username,))
        
        if mycursor.fetchone() != None:
            return "Username is already taken, please try with another username.", {"Refresh": "2; url=/signup"}


        password = request.form["password"]
        # image = request.files["picture"]

        sql = "INSERT INTO users (username, firstname, lastname, password) VALUES (%s, %s, %s, %s);"
        val = (username, firstname, lastname, password)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "added.")
        return "Account created.", {"Refresh": "2; url=/login"}

    return render_template("create-account.html")

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
    return render_template("create-post.html")

app.run(host="0.0.0.0", port=5000, debug=True)