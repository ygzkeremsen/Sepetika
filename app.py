from __future__ import annotations

import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "shop.db"
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-key-change-before-deployment")


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    connection = sqlite3.connect(DATABASE)
    connection.executescript("""
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin')),
        approved INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL CHECK(price >= 0),
        stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
        image TEXT NOT NULL DEFAULT '🛍️',
        active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        total REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Alındı',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL REFERENCES products(id),
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        unit_price REAL NOT NULL
    );
    """)
    if not connection.execute("SELECT 1 FROM users WHERE email='admin@magaza.local'").fetchone():
        connection.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                           ("Mağaza Yöneticisi", "admin@magaza.local", generate_password_hash("Admin123!"), "admin"))
    if connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        connection.executemany("INSERT INTO products(name,description,price,stock,image) VALUES(?,?,?,?,?)", [
            ("Kablosuz Kulaklık", "Günlük kullanım için konforlu Bluetooth kulaklık.", 1299.90, 18, "🎧"),
            ("Akıllı Saat", "Aktivite takibi ve bildirim özellikleri.", 2199.00, 12, "⌚"),
            ("Sırt Çantası", "Dayanıklı, geniş bölmeli şehir çantası.", 849.50, 25, "🎒"),
            ("Masa Lambası", "Çalışma alanları için ayarlanabilir LED lamba.", 579.00, 9, "💡"),
        ])
    connection.commit()
    connection.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Bu işlem için giriş yapmalısınız.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_cart_count():
    return {"cart_count": sum(session.get("cart", {}).values())}


@app.route("/")
def index():
    products = db().execute("SELECT * FROM products WHERE active=1 ORDER BY id DESC").fetchall()
    return render_template("index.html", products=products)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name, email, password = (request.form.get(k, "").strip() for k in ("name", "email", "password"))
        if not name or not email or len(password) < 8:
            flash("Tüm alanları doldurun; parola en az 8 karakter olmalıdır.", "error")
        else:
            try:
                db().execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                             (name, email.lower(), generate_password_hash(password)))
                db().commit()
                flash("Hesabınız oluşturuldu. Giriş yapabilirsiniz.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Bu e-posta adresi zaten kayıtlı.", "error")
    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email, password = request.form.get("email", "").strip().lower(), request.form.get("password", "")
        user = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and user["approved"] and check_password_hash(user["password_hash"], password):
            session.clear()
            session.update(user_id=user["id"], name=user["name"], role=user["role"], cart={})
            return redirect(url_for("admin" if user["role"] == "admin" else "index"))
        flash("Giriş bilgileri geçersiz veya hesabınız onay bekliyor.", "error")
    return render_template("auth.html", mode="login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    product = db().execute("SELECT * FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
    if not product:
        abort(404)
    cart = session.get("cart", {})
    key = str(product_id)
    quantity = int(request.form.get("quantity", 1))
    if quantity < 1 or quantity > product["stock"]:
        flash("İstenen miktar stokta bulunmuyor.", "error")
    else:
        cart[key] = min(cart.get(key, 0) + quantity, product["stock"])
        session["cart"] = cart
        flash("Ürün sepete eklendi.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart")
def cart():
    items, total = [], 0
    for product_id, quantity in session.get("cart", {}).items():
        product = db().execute("SELECT * FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
        if product:
            subtotal = product["price"] * quantity
            total += subtotal
            items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
    return render_template("cart.html", items=items, total=total)


@app.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart_data = session.get("cart", {})
    cart_data.pop(str(product_id), None)
    session["cart"] = cart_data
    return redirect(url_for("cart"))


@app.post("/checkout")
@login_required
def checkout():
    connection = db()
    cart_data = session.get("cart", {})
    if not cart_data:
        flash("Sepetiniz boş.", "warning")
        return redirect(url_for("cart"))
    try:
        connection.execute("BEGIN IMMEDIATE")
        rows = []
        for product_id, quantity in cart_data.items():
            product = connection.execute("SELECT * FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
            if not product or quantity > product["stock"]:
                raise ValueError("Stok miktarı değişti. Sepetinizi kontrol edin.")
            rows.append((product, quantity))
        total = sum(p["price"] * q for p, q in rows)
        cursor = connection.execute("INSERT INTO orders(user_id,total) VALUES(?,?)", (session["user_id"], total))
        for product, quantity in rows:
            connection.execute("INSERT INTO order_items(order_id,product_id,quantity,unit_price) VALUES(?,?,?,?)",
                               (cursor.lastrowid, product["id"], quantity, product["price"]))
            connection.execute("UPDATE products SET stock=stock-? WHERE id=?", (quantity, product["id"]))
        connection.commit()
        session["cart"] = {}
        flash("Siparişiniz alındı. Ödeme bu eğitim projesinde simüle edilir.", "success")
    except ValueError as error:
        connection.rollback()
        flash(str(error), "error")
    return redirect(url_for("orders"))


@app.route("/orders")
@login_required
def orders():
    rows = db().execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    return render_template("orders.html", orders=rows)


@app.route("/admin")
@admin_required
def admin():
    connection = db()
    products = connection.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    users = connection.execute("SELECT id,name,email,role,approved FROM users ORDER BY id").fetchall()
    orders_list = connection.execute("SELECT o.*,u.name AS customer FROM orders o JOIN users u ON u.id=o.user_id ORDER BY o.id DESC").fetchall()
    return render_template("admin.html", products=products, users=users, orders=orders_list)


@app.post("/admin/product")
@admin_required
def save_product():
    fields = [request.form.get(key, "").strip() for key in ("name", "description", "price", "stock", "image")]
    try:
        name, description, price, stock, image = fields
        if not name or not description or float(price) < 0 or int(stock) < 0:
            raise ValueError
        product_id = request.form.get("product_id")
        values = (name, description, float(price), int(stock), image or "🛍️")
        if product_id:
            db().execute("UPDATE products SET name=?,description=?,price=?,stock=?,image=? WHERE id=?", (*values, product_id))
        else:
            db().execute("INSERT INTO products(name,description,price,stock,image) VALUES(?,?,?,?,?)", values)
        db().commit()
        flash("Ürün kaydedildi.", "success")
    except (ValueError, sqlite3.Error):
        flash("Ürün bilgilerini kontrol edin.", "error")
    return redirect(url_for("admin"))


@app.post("/admin/product/<int:product_id>/toggle")
@admin_required
def toggle_product(product_id):
    db().execute("UPDATE products SET active=1-active WHERE id=?", (product_id,))
    db().commit()
    return redirect(url_for("admin"))


@app.post("/admin/user/<int:user_id>/approval")
@admin_required
def approve_user(user_id):
    db().execute("UPDATE users SET approved=1-approved WHERE id=? AND role='user'", (user_id,))
    db().commit()
    return redirect(url_for("admin"))


@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="Bu bölüme erişim yetkiniz yok."), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="Aradığınız sayfa bulunamadı."), 404


init_db()

if __name__ == "__main__":
    app.run(debug=True)
