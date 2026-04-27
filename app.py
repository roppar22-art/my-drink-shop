import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --- (သင့်ရဲ့ Token နဲ့ ID များကို ဒီမှာ ထည့်ပါ) ---
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

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
    {"id": 1, "name": "Espresso", "price": 3500, "img": "https://images.unsplash.com/photo-1510707577719-fa741c60299d?w=400"},
    {"id": 2, "name": "Cappuccino", "price": 5500, "img": "https://images.unsplash.com/photo-1534706936160-d5bb61c21f95?w=400"},
    {"id": 3, "name": "Latte", "price": 5000, "img": "https://images.unsplash.com/photo-1570968015849-18875329509a?w=400"},
    {"id": 4, "name": "Mocha", "price": 6000, "img": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400"}
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

@app.route('/checkout')
def checkout():
    if not session.get('cart'): return redirect(url_for('home'))
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
    
    send_telegram(f"🔔 အော်ဒါသစ်တက်ပြီ!\nID: #{order_id}\nဝယ်သူ: {name}\nမှာယူမှု: {item_names}")
    session.pop('cart', None)
    return render_template('success.html', order_id=order_id)

@app.route('/cancel/<int:id>')
def cancel(id):
    pw = request.args.get('pw')
    if pw != '1234': return "Denied"
    conn = sqlite3.connect('orders.db')
    c = conn.cursor(); c.execute("UPDATE orders SET status='Cancelled' WHERE id=?", (id,))
    conn.commit(); conn.close()
    send_telegram(f"❌ Order #{id} ကို Cancel လုပ်လိုက်ပါသည်။")
    return redirect(url_for('admin', pw=pw))

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != '1234': return "Wrong PW"
    conn = sqlite3.connect('orders.db')
    c = conn.cursor(); c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall(); conn.close()
    return render_template('admin.html', orders=orders, pw=pw)

@app.route('/track', methods=['GET', 'POST'])
def track():
    res = None
    if request.method == 'POST':
        oid = request.form.get('order_id')
        conn = sqlite3.connect('orders.db')
        c = conn.cursor(); c.execute("SELECT items, status FROM orders WHERE id=?", (oid,))
        res = c.fetchone(); conn.close()
    return render_template('track.html', res=res)
    
