import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (submitting the form)
    if request.method == "POST":
        # 1. Get the symbol from the form
        symbol = request.form.get("symbol")

        # 2. Check if the symbol is valid
        if not symbol:
            return apology("must provide symbol", 400)

        # 3. Call the lookup function to get stock data
        stock = lookup(symbol)

        # 4. Check if the lookup was successful
        if stock is None:
            return apology("invalid symbol", 400)

        # 5. Show the user the result on a new page
        return render_template("quoted.html", stock=stock)

    # User reached route via GET (clicking the "Quote" link)
    else:
        return render_template("quote.html")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (submitting the form)
    if request.method == "POST":

        # 1. Get and validate the symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)

        stock = lookup(symbol)
        if stock is None:
            return apology("invalid symbol", 400)

        # 2. Get and validate the number of shares
        shares_str = request.form.get("shares")
        if not shares_str:
            return apology("must provide shares", 400)

        try:
            shares = int(shares_str)
            if shares <= 0:
                return apology("shares must be a positive integer", 400)
        except ValueError:
            return apology("shares must be a number", 400)

        # 3. Check if the user can afford the purchase
        user_id = session["user_id"]
        user_cash_row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_row[0]["cash"]

        total_cost = stock["price"] * shares

        if user_cash < total_cost:
            return apology("can't afford purchase", 400)

        # 4. Update databases (user's cash and transactions table)

        # Subtract cash from user
        new_cash_balance = user_cash - total_cost
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_balance, user_id)

        # Add the transaction to the history
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, stock["symbol"], shares, stock["price"])

        # 5. Redirect to homepage
        flash("Bought!")
        return redirect("/")

    # User reached route via GET (clicking the "Buy" link)
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Get all transactions for the current user, ordered by most recent
    transactions = db.execute(
        "SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
        session["user_id"]
    )

    return render_template("history.html", transactions=transactions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Get the user's ID from the session
    user_id = session["user_id"]

    # 1. Get user's current cash balance
    user_cash_row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    user_cash = user_cash_row[0]["cash"]

    # 2. Get user's stock portfolio
    # We need to SUM the shares for each symbol, grouped by symbol.
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares " +
        "FROM transactions " +
        "WHERE user_id = ? " +
        "GROUP BY symbol " +
        "HAVING total_shares > 0",  # Only show stocks they still own
        user_id
    )

    # 3. Prepare data for the template
    portfolio = []
    grand_total = user_cash  # Start the grand total with the user's cash

    for stock in stocks:
        stock_data = lookup(stock["symbol"])
        current_price = stock_data["price"]
        total_value = current_price * stock["total_shares"]

        portfolio.append({
            "symbol": stock["symbol"],
            "shares": stock["total_shares"],
            "price": current_price,
            "total": total_value
        })

        grand_total += total_value

    # 4. Render the homepage with all the data
    return render_template("index.html", portfolio=portfolio, user_cash=user_cash, grand_total=grand_total)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (submitting the form)
    if request.method == "POST":

        # 1. Get form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # 2. Check for errors
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must confirm password", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)

        # 3. Check if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("username already taken", 400)

        # 4. Add the new user to the database
        # Hash the password
        password_hash = generate_password_hash(password)

        # Insert new user into the 'users' table
        # The 'users' table starts with 10000 cash by default
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)

        # 5. Log the new user in automatically
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]

        # 6. Redirect to the homepage
        flash("Registered successfully!")
        return redirect("/")

    # User reached route via GET (clicking the "Register" link)
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Get user's ID
    user_id = session["user_id"]

    # Get user's owned stocks for the dropdown menu
    stocks = db.execute(
        "SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id
    )

    # User reached route via POST (submitting the form)
    if request.method == "POST":

        # 1. Get and validate symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must select a stock", 400)

        # 2. Get and validate shares
        try:
            shares_to_sell = int(request.form.get("shares"))
            if shares_to_sell <= 0:
                return apology("shares must be a positive number", 400)
        except ValueError:
            return apology("shares must be a number", 400)

        # 3. Check if user owns enough shares
        row = db.execute(
            "SELECT SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            user_id, symbol
        )

        if not row or row[0]["total_shares"] < shares_to_sell:
            return apology("not enough shares", 400)

        # 4. Get current stock price
        stock = lookup(symbol)
        current_price = stock["price"]
        total_sale_value = current_price * shares_to_sell

        # 5. Get user's current cash
        user_cash_row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_row[0]["cash"]

        # 6. Update databases
        # Add cash to user's account
        db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash + total_sale_value, user_id)

        # Record the sale in transactions (as negative shares)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, stock["symbol"], -shares_to_sell, current_price)

        # 7. Redirect to homepage
        flash("Sold!")
        return redirect("/")

    # User reached route via GET (clicking the "Sell" link)
    else:
        return render_template("sell.html", stocks=stocks)
