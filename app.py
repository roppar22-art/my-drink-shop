import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- (သင့်ရဲ့ Token နဲ့ ID များကို ဒီနေရာမှာ ပြန်ထည့်ပါ) ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"
# ----------------------------------------------------

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url, timeout=10)
    except:
        pass

def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, drink TEXT)''')
    conn.commit()
    conn.close()

init_db()

DRINKS = [
    {"id": 1, "name": "Espresso", "price": 3500},
    {"id": 2, "name": "Cappuccino", "price": 5500},
    {"id": 3, "name": "Latte", "price": 5000},
    {"id": 4, "name": "Flat White", "price": 5000},
    {"id": 5, "name": "Macchiato", "price": 4500},
    {"id": 6, "name": "Mocha", "price": 6000},
    {"id": 7, "name": "Caramel Latte", "price": 6500},
    {"id": 8, "name": "Cold Coffee", "price": 5500},
    {"id": 9, "name": "Black Coffee", "price": 4000}
]

@app.route('/')
def home():
    return render_template('index.html', drinks=DRINKS)

@app.route('/order/<int:id>')
def order(id):
    drink = next((d for d in DRINKS if d['id'] == id), None)
    return render_template('checkout.html', drink=drink)

@app.route('/confirm', methods=['POST'])
def confirm():
    name = request.form.get('customer_name')
    address = request.form.get('address')
    drink_name = request.form.get('drink_name')
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (name, address, drink) VALUES (?, ?, ?)", (name, address, drink_name))
    conn.commit()
    conn.close()
    
    msg = f"🔔 အော်ဒါအသစ်တက်လာပါပြီ!\n\nဝယ်သူ: {name}\nမှာယူသည့်ပစ္စည်း: {drink_name}\nလိပ်စာ: {address}"
    send_telegram(msg)
    return render_template('success.html', drink_name=drink_name, address=address)

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != '1234': return "Wrong Password"
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()
    return render_template('admin.html', orders=orders, pw=pw)

# --- ပစ္စည်းမရှိလို့ အော်ဒါကို Cancel လုပ်မည့် Route ---
@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    pw = request.args.get('pw')
    if pw != '1234': return "Unauthorized"
    
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    
    # ဆိုင်မှာ ပစ္စည်းမရှိလို့ Cancel လုပ်လိုက်ကြောင်း Noti ပြန်ပို့လို့ရပါတယ်
    send_telegram(f"❌ Order #{order_id} ကို Cancel လုပ်လိုက်ပါပြီ။")
    
    return redirect(url_for('admin', pw=pw))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    
