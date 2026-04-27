# DRINKS စာရင်းမှာ category တွေ ထပ်ဖြည့်လိုက်ပါ
DRINKS = [
    {"id": 1, "name": "Classic Burger", "price": 8500, "img": "https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=500", "category": "BURGERS"},
    {"id": 2, "name": "Star Coffee", "price": 4500, "img": "https://images.unsplash.com/photo-1510707577719-fa741c60299d?w=500", "category": "COFFEE"},
    {"id": 3, "name": "French Fries", "price": 3000, "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500", "category": "SIDES"},
    {"id": 4, "name": "Vanilla Shake", "price": 5500, "img": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500", "category": "SHAKES"},
]

@app.route('/')
def home():
    cat = request.args.get('category', 'ALL')
    if cat == 'ALL':
        filtered_drinks = DRINKS
    else:
        filtered_drinks = [d for d in DRINKS if d['category'] == cat]
    return render_template('index.html', drinks=filtered_drinks, active_cat=cat)
    
