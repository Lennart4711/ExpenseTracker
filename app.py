from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from datetime import datetime, timedelta
from os import urandom

from config import Config
from models import Expense
from graphs import generate_plot
from utils import parse_price, most_used_categories, invalidate_old_sessions


# Create the Flask application
app = Flask(__name__)
app.config["ALLOW_OLD_SESSIONS"] = Config.ALLOW_OLD_SESSIONS
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///databases/expenses.db"
app.config["SESSION_TYPE"] = Config.SESSION_TYPE

if not app.config["ALLOW_OLD_SESSIONS"]:
    invalidate_old_sessions()
    
app.secret_key = urandom(24)
Session(app)


# Create the database connection
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)



@app.route("/password", methods=["GET", "POST"])
def password():
    if request.method == "POST":
        password = request.form.get("password")
        # Replace this with your actual password validation logic
        if password == Config.PASSWORD_HASH:
            session["authenticated"] = "authenticated"
            return redirect(url_for("index"))
        else:
            with open("logs/failed_logins.txt", "a") as f:
                f.write(f"{datetime.now()}; {request.remote_addr}; {password}\n")
                f.write(f"{request.form})\n")
    return render_template("password.html")


@app.route("/logout")
def logout():
    session["authenticated"] = False
    return redirect(url_for("password"))


def is_authenticated():
    return "authenticated" in session and session["authenticated"] == "authenticated"


@app.before_request
def before_request():
    try:
        if not is_authenticated() and not request.endpoint.startswith("static"):
            if request.endpoint != "password":
                return redirect(url_for("password"))
    except AttributeError:
        pass


@app.route("/")
def index():
    expenses = db_session.query(Expense).all()
    plot_data, balance = generate_plot(engine)
    categories = most_used_categories(4, db_session, Expense)

    insights = generate_insights()
    return render_template(
        "index.html",
        expenses=expenses,
        plot_data=plot_data,
        categories=categories,
        balance=balance,
        differences=insights,
    )


@app.route("/add_expense", methods=["POST"])
def add_expense():
    price = parse_price(request.form["price"])
    usage = request.form["usage"]
    date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
    category = request.form["category"]

    new_expense = Expense(price=price, usage=usage, date=date, category=category)
    db_session.add(new_expense)
    db_session.commit()

    return redirect(url_for("index"))


@app.route("/delete_latest", methods=["GET"])
def delete_latest():
    latest_expense = db_session.query(Expense).order_by(Expense.id.desc()).first()
    db_session.delete(latest_expense)
    db_session.commit()

    return redirect(url_for("index"))

def generate_insights():
    return [
        f"Your balanced changed {-get_difference(n)/100:.2f}€ compared to {n} days ago."
        for n in [1,2,4,7,10,14,20,30,31]
    ]

        
def get_difference(days) -> float:
    """Get the difference between the total balance today and the total balance days ago."""
    today = datetime.today()
    days_ago = today - timedelta(days=days)
    today = today.strftime("%Y-%m-%d")
    days_ago = days_ago.strftime("%Y-%m-%d")

    # Get the sum of all expenses till today
    expenses_till_today = db_session.query(Expense).filter(Expense.date <= today).all()
    expenses_till_today = sum([expense.price for expense in expenses_till_today])
    # Get the sum of all expenses till days ago
    expenses_till_days_ago = db_session.query(Expense).filter(
        Expense.date <= days_ago
    ).all()
    expenses_till_days_ago = sum([expense.price for expense in expenses_till_days_ago])
    return expenses_till_today - expenses_till_days_ago

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
