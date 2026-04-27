import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "tinzar-coffee-secret-key-2026"   # session အတွက်
Session(app)

# ==================== Telegram Settings ====================
BOT_TOKEN = "YOUR_BOT_TOKEN"      # သင့် token ထည့်ပါ
CHAT_ID = "YOUR_CHAT_ID"          # သင့် chat id ထည့်ပါ

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# ==================== Database ====================
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, address TEXT, items TEXT, 
                  total INTEGER, status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

init_db()

# ==================== Mock Menu Data (Coffee & Cakes) ====================
PRODUCTS = [
    {"id": 1, "name": "4 Treat Box", "price": 4800, "type": "combo", "desc": "Choose 2 coffees + 2 cakes", "img": "https://images.unsplash.com/photo-1607478900766-efe1326d7c58?w=500"},
    {"id": 2, "name": "6 Treat Box", "price": 7800, "type": "combo", "desc": "Choose 3 coffees + 3 cakes", "img": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=500"},
    {"id": 3, "name": "8 Treat Box", "price": 9800, "type": "combo", "desc": "Choose 4 coffees + 4 cakes", "img": "https://images.unsplash.com/photo-1535993401916-1a1e6bd65671?w=500"},
    {"id": 4, "name": "Classic Cheesecake", "price": 3200, "type": "cake", "desc": "New York style", "img": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500"},
    {"id": 5, "name": "Chocolate Fudge Cake", "price": 3500, "type": "cake", "desc": "Rich chocolate", "img": "https://images.unsplash.com/photo-1578985545062-69928b1d9582?w=500"},
    {"id": 6, "name": "Caramel Macchiato", "price": 2800, "type": "coffee", "desc": "Hot/Iced", "img": "https://images.unsplash.com/photo-1485808191679-5f86510682a1?w=500"},
    {"id": 7, "name": "Latte", "price": 2500, "type": "coffee", "desc": "Smooth espresso", "img": "https://images.unsplash.com/photo-1568649929103-28ff2f5b0e4c?w=500"},
]

# ==================== Routes ====================
@app.route('/')
def home():
    # category filter: all, combo, cake, coffee
    cat = request.args.get('category', 'all')
    if cat == 'all':
        products = PRODUCTS
    else:
        products = [p for p in PRODUCTS if p['type'] == cat]
    # ကြော်ငြာ banner အတွက် points ကို session ထဲကထုတ်
    points = session.get('loyalty_points', 0)
    logged_in = session.get('logged_in', False)
    return render_template('index.html', products=products, active_cat=cat, points=points, logged_in=logged_in)

@app.route('/api/get_cart')
def get_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return jsonify({'cart': cart, 'total': total, 'count': len(cart)})

@app.route('/api/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    # cart item structure: { id, name, price, customization, quantity }
    cart = session.get('cart', [])
    # add item
    new_item = {
        'id': data.get('id'),
        'name': data.get('name'),
        'price': data.get('price'),
        'customization': data.get('customization', 'Standard'),
        'quantity': 1
    }
    cart.append(new_item)
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/api/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    index = data.get('index')
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session['cart'] = cart
        session.modified = True
    return jsonify({'success': True})

@app.route('/api/join_points', methods=['POST'])
def join_points():
    # 500 bonus points
    session['loyalty_points'] = session.get('loyalty_points', 0) + 500
    session.modified = True
    return jsonify({'points': session['loyalty_points']})

@app.route('/api/login', methods=['POST'])
def login():
    # demo login - any username/password
    session['logged_in'] = True
    session['loyalty_points'] = session.get('loyalty_points', 0) + 100   # login bonus
    session.modified = True
    return jsonify({'success': True, 'points': session['loyalty_points']})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if not session.get('cart'):
        return redirect(url_for('home'))
    name = request.form.get('name')
    address = request.form.get('address')
    cart = session.get('cart', [])
    items_str = "\n".join([f"{item['name']} (x1) - {item['customization']}" for item in cart])
    total = sum(item['price'] for item in cart)
    
    # save to db
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (name, address, items, total) VALUES (?, ?, ?, ?)",
              (name, address, items_str, total))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Telegram သို့ပို့
    send_telegram(f"☕ Tinzar Order #{order_id}\nName: {name}\nAddress: {address}\nItems:\n{items_str}\nTotal: {total/100:.2f} USD")
    
    session.pop('cart', None)
    # checkout ပြီးရင် double points (Tornado)
    if session.get('tornado_double', False):
        session['loyalty_points'] = session.get('loyalty_points', 0) + (total // 100) * 2
    else:
        session['loyalty_points'] = session.get('loyalty_points', 0) + (total // 100)
    session.modified = True
    return redirect(url_for('history'))

@app.route('/history')
def history():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT id, items, total, status FROM orders ORDER BY id DESC LIMIT 20")
    orders = c.fetchall()
    conn.close()
    return render_template('history.html', orders=orders)

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != '1234':
        return "Access Denied"
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

if __name__ == '__main__':
    app.run(debug=True)
