from flask import Flask, render_template, request, redirect, session
import uuid

app = Flask(__name__)
app.secret_key = 'tinzar_secret_key'

# Sample Menu Data
drinks = [
    {'id': 1, 'name': 'Espresso', 'price': 3500, 'category': 'COFFEE', 'emoji': '☕'},
    {'id': 2, 'name': 'Iced Latte', 'price': 4500, 'category': 'COFFEE', 'emoji': '🥤'},
    {'id': 3, 'name': 'Cheese Cake', 'price': 5500, 'category': 'CAKE', 'emoji': '🍰'},
    {'id': 4, 'name': 'Croissant', 'price': 3000, 'category': 'SNACK', 'emoji': '🥐'},
]

@app.route('/')
def index():
    if 'cart' not in session:
        session['cart'] = []
    cat = request.args.get('category', 'ALL')
    filtered = drinks if cat == 'ALL' else [d for d in drinks if d['category'] == cat]
    return render_template('index.html', drinks=filtered, active_cat=cat)

@app.route('/add_to_cart/<int:drink_id>')
def add_to_cart(drink_id):
    if 'cart' not in session:
        session['cart'] = []
    drink = next((d for d in drinks if d['id'] == drink_id), None)
    if drink:
        session['cart'].append(drink)
        session.modified = True
    return redirect('/')

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'history' not in session:
        session['history'] = []
    if session.get('cart'):
        order = {
            'id': str(uuid.uuid4())[:8],
            'items': session['cart'],
            'total': sum(d['price'] for d in session['cart'])
        }
        session['history'].append(order)
        session['cart'] = []
        session.modified = True
    return redirect('/history')

@app.route('/history')
def history():
    orders = session.get('history', [])
    return render_template('history.html', orders=orders)

# Hardee's UI Route
@app.route('/hardees')
def hardees():
    return render_template('hardees.html')

@app.route('/locations')
def locations():
    return """
    <div style="font-family:sans-serif; padding:40px; text-align:center;">
        <h2 style="color:#c8a96e;">Our Locations</h2>
        <div style="border:1px solid #ddd; padding:20px; border-radius:15px; display:inline-block;">
            <p>📍 <b>Bur Dubai Branch</b></p>
            <p>Al Rolla St, Bur Dubai, UAE</p>
            <p>📞 +971 50 000 0000</p>
            <p>⏰ 9:00 AM - 10:00 PM</p>
        </div><br><br>
        <a href="/" style="text-decoration:none; color:black; font-weight:bold;">← Back to Menu</a>
    </div>
    """

@app.route('/track_order')
def track_order():
    return """
    <div style="font-family:sans-serif; padding:40px; text-align:center;">
        <h2 style="color:#c8a96e;">Track Order</h2>
        <div style="border:1px solid #ddd; padding:20px; border-radius:15px; display:inline-block; width:300px;">
            <p style="font-size:12px; color:gray;">Order ID: #TZ-9921</p>
            <p style="font-weight:bold; font-size:20px;">Status: Brewing... ☕</p>
            <div style="width:100%; background:#eee; height:10px; border-radius:5px; margin:15px 0;">
                <div style="width:60%; background:#c8a96e; height:10px; border-radius:5px;"></div>
            </div>
            <p>Driver is arriving in <b>12 mins</b></p>
        </div><br><br>
        <a href="/" style="text-decoration:none; color:black; font-weight:bold;">← Back to Menu</a>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)
