import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Crear la aplicación
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configurar base de datos
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DATA_DIR, "inventory.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos
db = SQLAlchemy(app)

# ========== MODELOS ==========
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), default='')
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    type = db.Column(db.String(20))  # 'entrada' o 'salida'
    quantity = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='movements')

# ========== RUTAS PRINCIPALES ==========
@app.route('/')
def index():
    return render_template('index.html')

# ========== API RUTAS PARA PRODUCTOS (CON CATEGORÍA) ==========

@app.route('/api/products', methods=['GET'])
def api_get_products():
    products = Product.query.all()
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'code': p.code,
            'name': p.name,
            'description': p.description or '',
            'price': p.price,
            'quantity': p.stock,
            'category': p.category.name if p.category else 'General'
        })
    return jsonify(result)

@app.route('/api/products', methods=['POST'])
def api_add_product():
    data = request.get_json()
    
    # Generar código automático si no viene
    code = data.get('code')
    if not code:
        code = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Buscar categoría por nombre o crear una nueva
    category_name = data.get('category', 'General')
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        category = Category(name=category_name)
        db.session.add(category)
        db.session.commit()
    
    product = Product(
        code=code,
        name=data['name'],
        description=data.get('description', ''),
        price=float(data['price']),
        stock=int(data.get('quantity', 0)),
        category=category
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'success': True, 'id': product.id})

@app.route('/api/products/<int:id>', methods=['PUT'])
def api_update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = float(data['price'])
    if 'quantity' in data:
        product.stock = int(data['quantity'])
    if 'category' in data:
        category = Category.query.filter_by(name=data['category']).first()
        if not category:
            category = Category(name=data['category'])
            db.session.add(category)
            db.session.commit()
        product.category = category
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/products/<int:id>', methods=['DELETE'])
def api_delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True})

# ========== API RUTAS PARA MOVIMIENTOS ==========

@app.route('/api/movements', methods=['POST'])
def api_add_movement():
    data = request.get_json()
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    quantity = int(data['quantity'])
    if data['type'] == 'salida' and product.stock < quantity:
        return jsonify({'error': 'Stock insuficiente'}), 400
    
    if data['type'] == 'entrada':
        product.stock += quantity
    else:
        product.stock -= quantity
    
    movement = Movement(
        product_id=product.id,
        type=data['type'],
        quantity=quantity
    )
    db.session.add(movement)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/movements', methods=['GET'])
def api_get_movements():
    movements = Movement.query.order_by(Movement.date.desc()).limit(50).all()
    result = []
    for m in movements:
        result.append({
            'id': m.id,
            'product_name': m.product.name,
            'type': m.type,
            'quantity': m.quantity,
            'date': m.date.strftime('%d/%m/%Y %H:%M')
        })
    return jsonify(result)

# ========== RUTAS DE CATEGORÍAS ==========

@app.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash('❌ Ya existe una categoría con ese nombre', 'error')
            return redirect(url_for('add_category'))
        
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        flash('✅ Categoría agregada exitosamente', 'success')
        return redirect(url_for('categories'))
    
    return render_template('add_category.html')

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form['name']
        category.description = request.form.get('description', '')
        db.session.commit()
        flash('✅ Categoría actualizada', 'success')
        return redirect(url_for('categories'))
    
    return render_template('edit_category.html', category=category)

@app.route('/delete_category/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    if category.products:
        flash(f'❌ No se puede eliminar "{category.name}" porque tiene productos asociados', 'error')
        return redirect(url_for('categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash(f'✅ Categoría "{category.name}" eliminada', 'success')
    return redirect(url_for('categories'))

# ========== API RUTAS DE CATEGORÍAS ==========

@app.route('/api/categories', methods=['GET'])
def api_get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        result.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'product_count': len(c.products)
        })
    return jsonify(result)

@app.route('/api/categories', methods=['POST'])
def api_add_category():
    data = request.get_json()
    category = Category(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({'success': True, 'id': category.id})

# ========== EJECUTAR ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)