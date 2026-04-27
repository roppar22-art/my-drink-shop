import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --- Configuration ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=10)
    except: pass

def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, items TEXT, status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

init_db()

DRINKS = [
    {"id": 1, "name": "Classic Burger", "price": 8500, "img": "https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=500", "category": "BURGERS"},
    {"id": 2, "name": "Star Coffee", "price": 4500, "img": "https://images.unsplash.com/photo-1510707577719-fa741c60299d?w=500", "category": "COFFEE"},
    {"id": 3, "name": "French Fries", "price": 3000, "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500", "category": "SIDES"},
    {"id": 4, "name": "Vanilla Shake", "price": 5500, "img": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500", "category": "SHAKES"},
]

@app.route('/')
def home():
    cat = request.args.get('category', 'ALL')
    filtered = DRINKS if cat == 'ALL' else [d for d in DRINKS if d['category'] == cat]
    return render_template('index.html', drinks=filtered, active_cat=cat)

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

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/confirm', methods=['POST'])
def confirm():
    name, addr = request.form.get('customer_name'), request.form.get('address')
    items = session.get('cart', [])
    item_names = ", ".join([i['name'] for i in items])
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (name, address, items) VALUES (?, ?, ?)", (name, addr, item_names))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    send_telegram(f"🔔 Order New: #{order_id}\nName: {name}\nItems: {item_names}")
    session.pop('cart', None)
    return render_template('success.html', order_id=order_id)

@app.route('/history')
def history():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT id, items, status FROM orders ORDER BY id DESC LIMIT 10")
    orders = c.fetchall()
    conn.close()
    return render_template('history.html', orders=orders)

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

@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):
    pw = request.args.get('pw')
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()
    send_telegram(f"📢 Order #{id} status changed to {status}")
    return redirect(url_for('admin', pw=pw))

if __name__ == "__main__":
    app.run(debug=True)
    
