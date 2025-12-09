from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Product(db.Model):
    """Product model for inventory management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'price': self.price,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])


@app.route('/api/products', methods=['POST'])
def add_product():
    """Add a new product"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('price'):
        return jsonify({'error': 'Name and price are required'}), 400
    
    if float(data['price']) <= 0:
        return jsonify({'error': 'Price must be a positive number'}), 400
    
    if int(data.get('quantity', 0)) < 0:
        return jsonify({'error': 'Quantity cannot be negative'}), 400
    
    try:
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            quantity=int(data.get('quantity', 0)),
            price=float(data['price']),
            category=data.get('category', 'General')
        )
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product quantity"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if 'quantity' not in data:
        return jsonify({'error': 'Quantity is required'}), 400
    
    try:
        new_quantity = int(data['quantity'])
        if new_quantity < 0:
            return jsonify({'error': 'Quantity cannot be negative'}), 400
        product.quantity = new_quantity
        db.session.commit()
        return jsonify(product.to_dict())
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity value'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def init_db():
    """Initialize database with sample products"""
    with app.app_context():
        db.create_all()
        
        # Check if database is already populated
        if Product.query.count() > 0:
            print("Database already populated")
            return
        
        # Sample products
        sample_products = [
            {'name': 'Laptop', 'description': 'High-performance laptop for work and gaming', 'quantity': 15, 'price': 1299.99, 'category': 'Electronics'},
            {'name': 'Wireless Mouse', 'description': 'Ergonomic wireless mouse with precision tracking', 'quantity': 50, 'price': 29.99, 'category': 'Electronics'},
            {'name': 'Mechanical Keyboard', 'description': 'RGB mechanical keyboard with cherry switches', 'quantity': 30, 'price': 149.99, 'category': 'Electronics'},
            {'name': 'Monitor 27"', 'description': '4K UHD monitor with HDR support', 'quantity': 20, 'price': 399.99, 'category': 'Electronics'},
            {'name': 'USB-C Cable', 'description': 'Durable USB-C charging cable 6ft', 'quantity': 100, 'price': 12.99, 'category': 'Accessories'},
            {'name': 'Desk Lamp', 'description': 'LED desk lamp with adjustable brightness', 'quantity': 40, 'price': 34.99, 'category': 'Office'},
            {'name': 'Office Chair', 'description': 'Ergonomic office chair with lumbar support', 'quantity': 25, 'price': 249.99, 'category': 'Furniture'},
            {'name': 'Standing Desk', 'description': 'Electric adjustable standing desk', 'quantity': 10, 'price': 599.99, 'category': 'Furniture'},
            {'name': 'Webcam HD', 'description': '1080p HD webcam with auto-focus', 'quantity': 35, 'price': 79.99, 'category': 'Electronics'},
            {'name': 'Headphones', 'description': 'Noise-cancelling wireless headphones', 'quantity': 45, 'price': 199.99, 'category': 'Electronics'},
            {'name': 'Phone Stand', 'description': 'Adjustable phone stand for desk', 'quantity': 60, 'price': 15.99, 'category': 'Accessories'},
            {'name': 'Notebook Set', 'description': 'Set of 3 premium notebooks', 'quantity': 80, 'price': 19.99, 'category': 'Stationery'},
            {'name': 'Pen Set', 'description': 'Professional pen set with case', 'quantity': 70, 'price': 24.99, 'category': 'Stationery'},
            {'name': 'Whiteboard', 'description': 'Magnetic whiteboard 36x24 inches', 'quantity': 15, 'price': 49.99, 'category': 'Office'},
            {'name': 'Portable SSD 1TB', 'description': 'Fast external SSD with USB-C', 'quantity': 28, 'price': 129.99, 'category': 'Storage'},
            {'name': 'Power Bank', 'description': '20000mAh portable power bank', 'quantity': 55, 'price': 39.99, 'category': 'Accessories'},
            {'name': 'HDMI Cable', 'description': '4K HDMI cable 10ft', 'quantity': 90, 'price': 14.99, 'category': 'Accessories'},
            {'name': 'Laptop Stand', 'description': 'Aluminum laptop stand with cooling', 'quantity': 42, 'price': 44.99, 'category': 'Accessories'},
            {'name': 'Desk Organizer', 'description': 'Multi-compartment desk organizer', 'quantity': 65, 'price': 22.99, 'category': 'Office'},
            {'name': 'Cable Management Box', 'description': 'Hide and organize cables efficiently', 'quantity': 38, 'price': 18.99, 'category': 'Accessories'}
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"Database initialized with {len(sample_products)} products")


if __name__ == '__main__':
    init_db()
    # NOTE: debug=True is for development only. Set to False in production.
    # For production, use a WSGI server like gunicorn instead.
    app.run(debug=True, host='0.0.0.0', port=5000)
