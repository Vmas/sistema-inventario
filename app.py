import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Crear la aplicación
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configurar base de datos
# Configurar base de datos (PostgreSQL en Railway, SQLite local)
if getattr(sys, 'frozen', False):
    # Si es .exe, usar SQLite local
    BASE_DIR = os.path.dirname(sys.executable)
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DATA_DIR, "inventory.db")}'
else:
    # Si es Railway (o desarrollo), usar variable de entorno
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Reemplazar 'postgres://' con 'postgresql://' para SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://')
    else:
        # Si no hay DATABASE_URL, usar SQLite local (para desarrollo)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATA_DIR = os.path.join(BASE_DIR, 'data')
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DATA_DIR, "inventory.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    type = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='movements')

# ========== RUTAS ==========
@app.route('/')
def index():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

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
    code = data.get('code') or f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
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
    
    movement = Movement(product_id=product.id, type=data['type'], quantity=quantity)
    db.session.add(movement)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        
        if Category.query.filter_by(name=name).first():
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

# ========== REPORTES ==========
@app.route('/inventario_fisico')
def inventario_fisico():
    products = Product.query.all()
    data = []
    for p in products:
        ingresos = sum(m.quantity for m in p.movements if m.type == 'entrada')
        egresos = sum(m.quantity for m in p.movements if m.type == 'salida')
        diferencia = p.stock + ingresos - egresos
        estado = '⚠️ STOCK BAJO' if p.stock <= 5 else '✅ NORMAL'
        data.append({
            'codigo': p.code,
            'descripcion': p.name,
            'cantidad_existente': p.stock,
            'ingreso_mensual': ingresos,
            'egreso_mensual': egresos,
            'diferencia': diferencia,
            'estado': estado
        })
    
    return render_template('inventario_fisico.html', data=data, fecha=datetime.now().strftime('%d/%m/%Y'), hora=datetime.now().strftime('%H:%M'))

@app.route('/control_es')
def control_es():
    movements = Movement.query.order_by(Movement.date.desc()).limit(50).all()
    entradas = []
    salidas = []
    for m in movements:
        if m.type == 'entrada':
            entradas.append({'codigo': m.product.code, 'descripcion': m.product.name, 'cantidad': m.quantity, 'fecha': m.date.strftime('%d/%m/%Y'), 'hora': m.date.strftime('%H:%M'), 'firma': '______'})
        else:
            salidas.append({'codigo': m.product.code, 'descripcion': m.product.name, 'cantidad': m.quantity, 'fecha': m.date.strftime('%d/%m/%Y'), 'hora': m.date.strftime('%H:%M'), 'firma': '______'})
    
    return render_template('control_es.html', entradas=entradas, salidas=salidas, fecha=datetime.now().strftime('%d/%m/%Y'))

# ========== EJECUTAR ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)