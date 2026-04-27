import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "coffee_secret_key" # Required for Shopping Cart

# --- Configuration ---
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    # Added 'status' to track if order is Pending or Cancelled
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, items TEXT, status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

init_db()

DRINKS = [
    {"id": 1, "name": "Espresso", "price": 3500, "img": "https://images.unsplash.com/photo-1510707577719-fa741c60299d?w=500"},
    {"id": 2, "name": "Cappuccino", "price": 5500, "img": "https://images.unsplash.com/photo-1534706936160-d5bb61c21f95?w=500"},
    {"id": 3, "name": "Latte", "price": 5000, "img": "https://images.unsplash.com/photo-1570968015849-18875329509a?w=500"},
    {"id": 8, "name": "Cold Coffee", "price": 5500, "img": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=500"},
    {"id": 9, "name": "Black Coffee", "price": 4000, "img": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500"}
]

@app.route('/')
def home():
    return render_template('index.html', drinks=DRINKS)

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session: session['cart'] = []
    drink = next((d for d in DRINKS if d['id'] == id), None)
    if drink:
        session['cart'].append(drink)
        session.modified = True
    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    items = session.get('cart', [])
    total = sum(item['price'] for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/confirm', methods=['POST'])
def confirm():
    name = request.form.get('customer_name')
    address = request.form.get('address')
    cart_items = session.get('cart', [])
    item_names = ", ".join([i['name'] for i in cart_items])
    
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (name, address, items) VALUES (?, ?, ?)", (name, address, item_names))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    
    session.pop('cart', None) # Clear cart after order
    return render_template('success.html', order_id=order_id)

@app.route('/track', methods=['GET', 'POST'])
def track():
    order = None
    if request.method == 'POST':
        oid = request.form.get('order_id')
        conn = sqlite3.connect('orders.db')
        c = conn.cursor()
        c.execute("SELECT items, status FROM orders WHERE id=?", (oid,))
        order = c.fetchone()
        conn.close()
    return render_template('track.html', order=order)

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != '1234': return "Access Denied"
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()
    return render_template('admin.html', orders=orders, pw=pw)

@app.route('/cancel/<int:id>')
def cancel(id):
    pw = request.args.get('pw')
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status='Cancelled (Out of Stock)' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', pw=pw))

if __name__ == "__main__":
    app.run(debug=True)
    
