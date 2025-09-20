from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required, apology

app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # forget any user_id
    session.clear()
    
    if request.method == "GET":
        return render_template("login.html")
    
    else:
        # get user inputs
        username = request.form.get("username")
        password = request.form.get("password")
        
        # input validation
        if not username or not password:
            return apology("All fields must be filled!", 403)
        
        # check db for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        
        # check if the username & hashed password matches
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], password):
            return apology("Invalid Username/Password Combination!")
        
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    
@app.route("/logout")
def logout():
    # clear any user_id
    session.clear()
    return redirect("/")
            

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # get user input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        # input validation
        if username == "" or password == "" or confirmation == "":
            return apology("All fields need to be filled", 403)
        elif password != confirmation:
            return apology("Password and Re-type Password must match!", 403)
        
        # check if the user already exists
        existing_user = db.execute("SELECT username FROM users WHERE username = ?", username)
        
        if existing_user:
            return apology("Username not Available!", 403)
        
        password_hash = generate_password_hash(password, method="pbkdf2", salt_length=16)
        
        result = db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", username, password_hash)
        
        if result:
            # get user id and login the user automatically
            user_data = db.execute("SELECT id FROM users WHERE username = ?", username)
            
            if user_data:
                session["user_id"] = user_data[0]["id"]
                return redirect("/")
            else:
                return apology("Something went wrong!")
        


if __name__ == "__main__":
    app.run(debug=True)