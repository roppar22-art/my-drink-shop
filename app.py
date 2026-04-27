import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- (သင့်ရဲ့ Token နဲ့ ID တွေကို ဒီနေရာမှာ ပြန်ထည့်ပါ) ---
BOT_TOKEN = "ဒီမှာ_သင်ရလာတဲ့_Token_ထည့်ပါ"
CHAT_ID = "ဒီမှာ_သင့်ရဲ့_ID_နံပါတ်_ထည့်ပါ"
# ----------------------------------------------------

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url, timeout=10) # Timeout ထည့်ထားခြင်းဖြင့် အကြာကြီးမစောင့်ရအောင်
    except Exception as e:
        print(f"Telegram error: {e}")

# Database initialization
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, drink TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ပစ္စည်းစာရင်း (id တွေ မှားမသွားအောင် သတိထားပါ)
DRINKS = [
    {"id": 1, "name": "🍵 Green Tea", "price": 5000},
    {"id": 2, "name": "🧋 Milk Tea", "price": 5500},
    {"id": 3, "name": "☕️ Coffee", "price": 4500}
]

@app.route('/')
def home():
    # {{ "{:,}".format(drink.price) }} Ks လို့ သုံးနိုင်အောင် context processor မှာ ထည့်ပေးရပါတယ်
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
    
    # Database
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (name, address, drink) VALUES (?, ?, ?)", (name, address, drink_name))
    conn.commit()
    conn.close()
    
    # Telegram
    msg = f"🔔 အော်ဒါအသစ်တက်လာပါပြီ!\n\nဝယ်သူ: {name}\nမှာယူသည့်ပစ္စည်း: {drink_name}\nလိပ်စာ: {address}"
    send_telegram(msg)
    
    return f"""
    <div style="text-align:center; font-family:sans-serif; padding:50px;">
        <h1 style="color:green;">မှာယူမှု အောင်မြင်ပါသည်!</h1>
        <p>လူကြီးမင်းမှာယူသော <b>{drink_name}</b> ကို <b>{address}</b> သို့ မကြာမီ ပို့ဆောင်ပေးပါမည်။</p>
        <p>Cash on Delivery (ပစ္စည်းရောက်မှ ငွေချေပါ)</p>
        <br>
        <a href="/" style="text-decoration:none; color:blue;">🔙 ဆိုင်သို့ပြန်သွားရန်</a>
    </div>
    """

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != '1234':
        return "<h1>ဝင်ခွင့်မရှိပါ!</h1><p>Admin password မှားယွင်းနေပါသည်။</p>"
    
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    all_orders = c.fetchall()
    conn.close()
    return render_template('admin.html', orders=all_orders, pw=pw)

@app.route('/delete/<int:id>')
def delete_order(id):
    pw = request.args.get('pw')
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', pw=pw))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    
