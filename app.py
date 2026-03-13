from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "canteen_secret_key"

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("database.db")

def create_tables():
    con = get_db()
    cur = con.cursor()

    # Main Orders Table (One token per customer)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER,
            total_amount INTEGER,
            payment TEXT,
            date TEXT
        )
    """)

    # Items Table (Multiple items under one order)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            food TEXT,
            price INTEGER,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    """)

    con.commit()
    con.close()

create_tables()

# ---------------- USER ROUTES ----------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/order", methods=["POST"])
def order():
    foods = request.form.getlist("food")
    prices = request.form.getlist("price")
    payment = request.form["payment"]

    if not foods:
        return "No items selected"

    token = random.randint(1000, 9999)
    date = datetime.now().strftime("%Y-%m-%d")
    total_amount = sum([int(p) for p in prices])

    con = get_db()
    cur = con.cursor()

    cur.execute(
        "INSERT INTO orders (token, total_amount, payment, date) VALUES (?, ?, ?, ?)",
        (token, total_amount, payment, date)
    )

    order_id = cur.lastrowid

    for food, price in zip(foods, prices):
        cur.execute(
            "INSERT INTO order_items (order_id, food, price) VALUES (?, ?, ?)",
            (order_id, food, price)
        )

    con.commit()
    con.close()

    # ⭐ PAYMENT CHECK
    if payment == "online":
        session["token"] = token
        return redirect("/payment")

    return render_template("order_success.html", token=token)

      
# ---------------- PAYMENT ----------------
@app.route("/payment")
def payment():
    return render_template("payment.html")


@app.route("/confirm-payment", methods=["POST"])
def confirm_payment():
    token = session.get("token")
    return render_template("order_success.html", token=token)
# ---------------- ADMIN LOGIN ----------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/dashboard")
        else:
            return render_template("admin_login.html", error="Wrong password")

    return render_template("admin_login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin-login")

    search_token = request.args.get("token")
    today_filter = request.args.get("today")

    con = get_db()
    cur = con.cursor()

    # FILTER LOGIC
    if search_token:
        cur.execute("""
            SELECT * FROM orders 
            WHERE token=? 
            ORDER BY id DESC
        """, (search_token,))
    elif today_filter:
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute("""
            SELECT * FROM orders 
            WHERE date=? 
            ORDER BY id DESC
        """, (today,))
    else:
        cur.execute("""
            SELECT * FROM orders 
            ORDER BY id DESC
        """)

    orders = cur.fetchall()

    order_list = []

    for order in orders:
        cur.execute("SELECT food FROM order_items WHERE order_id=?", (order[0],))
        items = cur.fetchall()

        item_names = ", ".join([item[0] for item in items])

        order_list.append({
            "id": order[0],
            "token": order[1],
            "total": order[2],
            "payment": order[3],
            "date": order[4],
            "item_list": item_names  # IMPORTANT FIX
        })

    con.close()

    return render_template("admin_dashboard.html", orders=order_list)

# ---------------- DELIVER + BILL ----------------
@app.route("/deliver/<int:order_id>")
def deliver(order_id):
    if not session.get("admin"):
        return redirect("/admin-login")

    con = get_db()
    cur = con.cursor()

    # Get order
    cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = cur.fetchone()

    if not order:
        con.close()
        return "Order not found"

    # Get items
    cur.execute("SELECT food, price FROM order_items WHERE order_id=?", (order_id,))
    items = cur.fetchall()

    # Delete after delivery
    cur.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
    cur.execute("DELETE FROM orders WHERE id=?", (order_id,))

    con.commit()
    con.close()

    return render_template("bill.html", order=order, items=items)

# ---------------- REPORT ----------------
@app.route("/report")
def report():
    if not session.get("admin"):
        return redirect("/admin-login")

    con = get_db()
    cur = con.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")
    year = datetime.now().strftime("%Y")

    # ---------------- DAY WISE ----------------
    cur.execute("SELECT SUM(total_amount) FROM orders WHERE date=?", (today,))
    day_revenue = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM orders WHERE date=?", (today,))
    day_orders = cur.fetchone()[0]

    cur.execute("""
        SELECT order_items.food,
               COUNT(order_items.food),
               orders.date
        FROM order_items
        JOIN orders ON order_items.order_id = orders.id
        WHERE orders.date=?
        GROUP BY order_items.food, orders.date
    """, (today,))
    day_items = cur.fetchall()

    # ---------------- MONTH WISE ----------------
    cur.execute("SELECT SUM(total_amount) FROM orders WHERE date LIKE ?", (month + "%",))
    month_revenue = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT order_items.food,
               COUNT(order_items.food),
               orders.date
        FROM order_items
        JOIN orders ON order_items.order_id = orders.id
        WHERE orders.date LIKE ?
        GROUP BY order_items.food, orders.date
    """, (month + "%",))
    month_items = cur.fetchall()

    # ---------------- YEAR WISE ----------------
    cur.execute("SELECT SUM(total_amount) FROM orders WHERE date LIKE ?", (year + "%",))
    year_revenue = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT order_items.food,
               COUNT(order_items.food),
               orders.date
        FROM order_items
        JOIN orders ON order_items.order_id = orders.id
        WHERE orders.date LIKE ?
        GROUP BY order_items.food, orders.date
    """, (year + "%",))
    year_items = cur.fetchall()

    con.close()

    return render_template(
        "report.html",
        day_revenue=day_revenue,
        day_orders=day_orders,
        day_items=day_items,
        month_revenue=month_revenue,
        month_items=month_items,
        year_revenue=year_revenue,
        year_items=year_items
    )
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
