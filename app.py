from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

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

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    
    # Get user_id
    user_id = session.get("user_id")
    
    if request.method == "GET":
        
        # Get user details from db to display
        user_details = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        username = user_details[0]["username"]
        current_hour = datetime.now().hour
        greeting = ""
        
        if 5 <= current_hour < 12:
            greeting = f"Good Morning, {username}!"
        elif 12 <= current_hour < 18:
            greeting = f"Good Afternoon, {username}!"
        else:
            greeting = f"Good Evening, {username}!"
        
        return render_template("index.html", greeting=greeting)
    
    else:
        type = request.form.get("type")
        amount_str = float(request.form.get("amount"))
        description = request.form.get("description")
        date = request.form.get("date")
        category = request.form.get("category")
        
        if type not in ["income", "expense"]:
            return apology("Invalid Transaction Type!")

        # Validate amount
        try:
            amount = float(amount_str)  # convert string to float
            if amount < 0:
                return apology("Amount must be positive!")
        except ValueError:
            return apology("Invalid Transaction Amount!")  # not a number

        if not description:
            return apology("Description empty!")
        if not date:
            return apology("Date empty!")
        if not category:
            return apology("Category empty!")
        
        # Enter transaction into the db
        result = db.execute("INSERT INTO transactions (user_id, type, amount, description, date, category) VALUES (?, ?, ?, ?, ?, ?)", user_id, type, amount, description, date, category)
        
        if result:
            user_details = db.execute("SELECT * FROM users WHERE id = ?", user_id)
            cash_balance_before = user_details[0]["cash"]
            new_cash_balance = cash_balance_before
            
            if type == "income":
                new_cash_balance += amount
            else:
                new_cash_balance -= amount
            
            # update user cash balance after transaction
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_balance, user_id)
            
            flash("Transaction Successfull!", "success")
            return redirect("/")
            
                
             

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
        

@app.route("/transactions")
@login_required
def transations():
    
    # get user_id
    user_id = session["user_id"]
    
    # retrieve transaction history of the user
    rows = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    
    # Convert UTC datetime to IST (+5:30)
    for row in rows:
        if row['datetime']:
            # parse the string from DB to datetime object
            utc_dt = datetime.strptime(row['datetime'], "%Y-%m-%d %H:%M:%S")
            # add 5 hours 30 minutes
            ist_dt = utc_dt + timedelta(hours=5, minutes=30)
            # format back to string for display
            row['datetime'] = ist_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template("transactions.html", rows=rows)





@app.route("/overview")
@login_required
def overview():
    user_id = session["user_id"]

    # Get cash balance of the user
    row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash_balance = row[0]["cash"]

    # get total income
    total_income = db.execute(
        "SELECT SUM(amount) as total FROM transactions WHERE user_id = ? AND type = 'income'", user_id
    )[0]["total"] or 0

    # get total expense
    total_expense = db.execute(
        "SELECT SUM(amount) as total FROM transactions WHERE user_id = ? AND type = 'expense'", user_id
    )[0]["total"] or 0

    return render_template("overview.html", total_income=total_income, total_expense=total_expense, cash_balance=cash_balance)



if __name__ == "__main__":
    app.run(debug=True)