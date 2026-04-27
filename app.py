from flask import Flask, render_template, request, redirect, session
import uuid

app = Flask(__name__)
app.secret_key = 'tinzar_secret_key'

# Menu Data
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

@app.route('/hardees')
def hardees():
    return render_template('hardees.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
