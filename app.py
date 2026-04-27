import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --- Telegram Settings ---
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=5)
    except: pass

def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, items TEXT, status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

init_db()

# သင့်ရဲ့ Menu ပစ္စည်းစာရင်း
DRINKS = [
    {"id": 1, "name": "4 Burger Box", "price": 5800, "img": "https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=500", "category": "Crave N' Save"},
    {"id": 2, "name": "6 Burger Box", "price": 7800, "img": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500", "category": "Crave N' Save"},
    {"id": 3, "name": "Classic Chicken", "price": 4500, "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500", "category": "Burgers"},
    {"id": 4, "name": "Iced Coffee", "price": 3500, "img": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=500", "category": "Beverages"},
]

@app.route('/')
def home():
    cat = request.args.get('category', "Crave N' Save")
    filtered = [d for d in DRINKS if d['category'] == cat]
    return render_template('index.html', drinks=filtered, active_cat=cat)

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session: session['cart'] = []
    item = next((d for d in DRINKS if d['id'] == id), None)
    if item:
        session['cart'].append(item)
        session.modified = True
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    items = session.get('cart', [])
    total = sum(i['price'] for i in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/checkout', methods=['POST'])
def checkout():
    name = request.form.get('name')
    address = request.form.get('address')
    items = session.get('cart', [])
    item_str = ", ".join([i['name'] for i in items])
    
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (name, address, items) VALUES (?, ?, ?)", (name, address, item_str))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    
    send_telegram(f"🔔 Order #{order_id}\nName: {name}\nItems: {item_str}")
    session.pop('cart', None)
    return redirect(url_for('history'))

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

@app.route('/update_status/<int:id>/<string:new_status>')
def update_status(id, new_status):
    pw = request.args.get('pw')
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?", (new_status, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', pw=pw))

if __name__ == "__main__":
    app.run(debug=True)
    
