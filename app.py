import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Database တည်ဆောက်ခြင်း
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, drink TEXT)''')
    conn.commit()
    conn.close()

init_db()

DRINKS = [
    {"id": 1, "name": "Green Tea", "price": 5000},
    {"id": 2, "name": "Milk Tea", "price": 5500},
    {"id": 3, "name": "Coffee", "price": 4500}
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
    return "<h1>မှာယူမှုအောင်မြင်ပါသည်!</h1><a href='/'>ဆိုင်သို့ပြန်သွားရန်</a>"

@app.route('/admin')
def admin():
    # Password ကို '1234' လို့ ပေးထားပါတယ်
    pw = request.args.get('pw')
    if pw != '1234':
        return "<h1>Admin Password မှားနေပါသည်!</h1>"
    
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()
    return render_template('admin.html', orders=orders, pw=pw)

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
    app.run(host='0.0.0.0', port=5000)
