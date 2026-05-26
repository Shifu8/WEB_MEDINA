import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'cloud-billing-system-secret-key-2026'

DATABASE = 'database.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        address TEXT DEFAULT ''
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        total REAL DEFAULT 0,
        FOREIGN KEY (client_id) REFERENCES clients (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (invoice_id) REFERENCES invoices (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )''')

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ('admin', generate_password_hash('admin123'))
        )

    conn.commit()
    conn.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---- Auth Routes ----

@app.route('/')
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash('Please enter username and password', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f'Welcome back, {username}!', 'success')
        return redirect(url_for('dashboard'))

    flash('Invalid username or password', 'error')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


# ---- Dashboard ----

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()

    products_count = conn.execute(
        "SELECT COUNT(*) as count FROM products"
    ).fetchone()['count']
    clients_count = conn.execute(
        "SELECT COUNT(*) as count FROM clients"
    ).fetchone()['count']
    invoices_count = conn.execute(
        "SELECT COUNT(*) as count FROM invoices"
    ).fetchone()['count']
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(total), 0) as total FROM invoices"
    ).fetchone()['total']

    recent_invoices = conn.execute(
        """SELECT i.*, c.name as client_name
           FROM invoices i
           JOIN clients c ON i.client_id = c.id
           ORDER BY i.id DESC LIMIT 5"""
    ).fetchall()

    low_stock = conn.execute(
        "SELECT * FROM products WHERE stock <= 5 ORDER BY stock ASC LIMIT 5"
    ).fetchall()

    conn.close()

    return render_template('dashboard.html',
                           products_count=products_count,
                           clients_count=clients_count,
                           invoices_count=invoices_count,
                           total_revenue=total_revenue,
                           recent_invoices=recent_invoices,
                           low_stock=low_stock)


# ---- Products CRUD ----

@app.route('/products')
@login_required
def products():
    conn = get_db()
    products_list = conn.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template('products.html', products=products_list)


@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def product_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '0')
        stock = request.form.get('stock', '0')

        if not name:
            flash('Product name is required', 'error')
            return render_template('product_form.html')

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            flash('Invalid price or stock value', 'error')
            return render_template('product_form.html')

        conn = get_db()
        conn.execute(
            "INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
            (name, description, price, stock)
        )
        conn.commit()
        conn.close()

        flash('Product added successfully', 'success')
        return redirect(url_for('products'))

    return render_template('product_form.html')


@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def product_edit(id):
    conn = get_db()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (id,)
    ).fetchone()

    if not product:
        conn.close()
        flash('Product not found', 'error')
        return redirect(url_for('products'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '0')
        stock = request.form.get('stock', '0')

        if not name:
            flash('Product name is required', 'error')
            return render_template('product_form.html', product=product)

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            flash('Invalid price or stock value', 'error')
            return render_template('product_form.html', product=product)

        conn.execute(
            "UPDATE products SET name=?, description=?, price=?, stock=? WHERE id=?",
            (name, description, price, stock, id)
        )
        conn.commit()
        conn.close()

        flash('Product updated successfully', 'success')
        return redirect(url_for('products'))

    conn.close()
    return render_template('product_form.html', product=product)


@app.route('/products/delete/<int:id>')
@login_required
def product_delete(id):
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('products'))


# ---- Clients CRUD ----

@app.route('/clients')
@login_required
def clients():
    conn = get_db()
    clients_list = conn.execute(
        "SELECT * FROM clients ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template('clients.html', clients=clients_list)


@app.route('/clients/add', methods=['GET', 'POST'])
@login_required
def client_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if not name:
            flash('Client name is required', 'error')
            return render_template('client_form.html')

        conn = get_db()
        conn.execute(
            "INSERT INTO clients (name, email, phone, address) VALUES (?, ?, ?, ?)",
            (name, email, phone, address)
        )
        conn.commit()
        conn.close()

        flash('Client added successfully', 'success')
        return redirect(url_for('clients'))

    return render_template('client_form.html')


@app.route('/clients/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def client_edit(id):
    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE id = ?", (id,)
    ).fetchone()

    if not client:
        conn.close()
        flash('Client not found', 'error')
        return redirect(url_for('clients'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if not name:
            flash('Client name is required', 'error')
            return render_template('client_form.html', client=client)

        conn.execute(
            "UPDATE clients SET name=?, email=?, phone=?, address=? WHERE id=?",
            (name, email, phone, address, id)
        )
        conn.commit()
        conn.close()

        flash('Client updated successfully', 'success')
        return redirect(url_for('clients'))

    conn.close()
    return render_template('client_form.html', client=client)


@app.route('/clients/delete/<int:id>')
@login_required
def client_delete(id):
    conn = get_db()
    conn.execute("DELETE FROM clients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Client deleted successfully', 'success')
    return redirect(url_for('clients'))


# ---- Invoices ----

@app.route('/invoices')
@login_required
def invoices():
    conn = get_db()
    invoices_list = conn.execute(
        """SELECT i.*, c.name as client_name
           FROM invoices i
           JOIN clients c ON i.client_id = c.id
           ORDER BY i.id DESC"""
    ).fetchall()
    conn.close()
    return render_template('invoices.html', invoices=invoices_list)


@app.route('/invoices/create', methods=['GET', 'POST'])
@login_required
def invoice_create():
    conn = get_db()
    clients_list = conn.execute(
        "SELECT * FROM clients ORDER BY name"
    ).fetchall()
    products_list = conn.execute(
        "SELECT * FROM products ORDER BY name"
    ).fetchall()

    if request.method == 'POST':
        client_id = request.form.get('client_id')
        if not client_id:
            flash('Please select a client', 'error')
            conn.close()
            return render_template('invoice_form.html',
                                   clients=clients_list,
                                   products=products_list)

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')

        items = []
        total = 0

        for i in range(len(product_ids)):
            pid = product_ids[i]
            qty = quantities[i]
            if not pid or not qty:
                continue
            try:
                pid = int(pid)
                qty = int(qty)
            except ValueError:
                continue
            if qty <= 0:
                continue

            product = conn.execute(
                "SELECT * FROM products WHERE id = ?", (pid,)
            ).fetchone()
            if product and qty <= product['stock']:
                price = product['price']
                subtotal = price * qty
                total += subtotal
                items.append((pid, qty, price))

        if not items:
            flash('No valid items to invoice', 'error')
            conn.close()
            return render_template('invoice_form.html',
                                   clients=clients_list,
                                   products=products_list)

        cursor = conn.execute(
            "INSERT INTO invoices (client_id, date, total) VALUES (?, ?, ?)",
            (client_id, date, total)
        )
        invoice_id = cursor.lastrowid

        for pid, qty, price in items:
            conn.execute(
                "INSERT INTO invoice_items (invoice_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (invoice_id, pid, qty, price)
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (qty, pid)
            )

        conn.commit()
        conn.close()

        flash('Invoice created successfully', 'success')
        return redirect(url_for('invoices'))

    conn.close()
    return render_template('invoice_form.html',
                           clients=clients_list,
                           products=products_list)


@app.route('/invoices/view/<int:id>')
@login_required
def invoice_view(id):
    conn = get_db()

    invoice = conn.execute(
        """SELECT i.*, c.name as client_name, c.email as client_email,
                  c.phone as client_phone, c.address as client_address
           FROM invoices i
           JOIN clients c ON i.client_id = c.id
           WHERE i.id = ?""",
        (id,)
    ).fetchone()

    if not invoice:
        conn.close()
        flash('Invoice not found', 'error')
        return redirect(url_for('invoices'))

    items = conn.execute(
        """SELECT ii.*, p.name as product_name
           FROM invoice_items ii
           JOIN products p ON ii.product_id = p.id
           WHERE ii.invoice_id = ?""",
        (id,)
    ).fetchall()

    conn.close()

    return render_template('invoice_view.html',
                           invoice=invoice,
                           items=items)


@app.route('/invoices/delete/<int:id>')
@login_required
def invoice_delete(id):
    conn = get_db()

    items = conn.execute(
        "SELECT * FROM invoice_items WHERE invoice_id = ?", (id,)
    ).fetchall()

    for item in items:
        conn.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (item['quantity'], item['product_id'])
        )

    conn.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (id,))
    conn.execute("DELETE FROM invoices WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash('Invoice deleted successfully', 'success')
    return redirect(url_for('invoices'))


@app.route('/api/products/<int:id>')
@login_required
def api_product(id):
    conn = get_db()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (id,)
    ).fetchone()
    conn.close()
    if product:
        return {
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'stock': product['stock']
        }
    return {'error': 'Product not found'}, 404


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
