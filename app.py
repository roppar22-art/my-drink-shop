import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database 初始化 (Database စတင်တည်ဆောက်ခြင်း)
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, 
                 items TEXT, total_price INTEGER, status TEXT DEFAULT 'Pending', 
                 order_date DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Menu Data (ဒါကို ပုံသေထားနိုင်သလို DB ထဲမှာလည်း သိမ်းနိုင်ပါတယ်)
DRINKS = [
    {"id": 1, "name": "Espresso", "price": 3500, "cat": "COFFEE", "emoji": "☕"},
    {"id": 2, "name": "Iced Latte", "price": 4500, "cat": "COFFEE", "emoji": "🥤"},
    {"id": 3, "name": "Matcha Cake", "price": 5500, "cat": "CAKE", "emoji": "🍰"},
    {"id": 4, "name": "Signature Croissant", "price": 3800, "cat": "SNACK", "emoji": "🥐"},
    {"id": 5, "name": "Chocolate Lava", "price": 6000, "cat": "CAKE", "emoji": "🌋"},
]

@app.route('/')
def index():
    # Category Filter
    cat = request.args.get('category', 'ALL')
    if cat == 'ALL':
        filtered_drinks = DRINKS
    else:
        filtered_drinks = [d for d in DRINKS if d['cat'] == cat]
    
    return render_template('index.html', drinks=filtered_drinks, active_cat=cat)

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session: session['cart'] = []
    drink = next((d for d in DRINKS if d['id'] == id), None)
    if drink:
        session['cart'].append(drink)
        session.modified = True
    return redirect(url_for('index'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('index'))
    
    items = ", ".join([i['name'] for i in session['cart']])
    total = sum(i['price'] for i in session['cart'])
    
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (customer_name, items, total_price) VALUES (?, ?, ?)", 
              ("Guest User", items, total))
    conn.commit()
    conn.close()
    
    session.pop('cart', None)
    return redirect(url_for('history'))

@app.route('/history')
def history():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 10")
    orders = c.fetchall()
    conn.close()
    return render_template('history.html', orders=orders)

@app.route('/admin')
def admin():
    # Admin အတွက် Password ကို 1234 လို့ သတ်မှတ်ထားပါတယ်
    pw = request.args.get('pw')
    if pw != '1234': return "Access Denied!"
    
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', pw='1234'))

if __name__ == '__main__':
    app.run(debug=True)
    
