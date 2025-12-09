# InventoryApp

A modern, web-based inventory management system built with Flask and SQLite. Manage your product inventory with an intuitive interface that allows you to browse, add, delete, and update product quantities.

## Features

- 📦 **Browse Products** - View all products in a modern, card-based layout
- ➕ **Add Products** - Easily add new products with details like name, description, price, quantity, and category
- 🗑️ **Delete Products** - Remove products from inventory with confirmation
- 🔢 **Update Quantities** - Adjust product quantities with intuitive +/- controls or direct input
- 🔍 **Search & Filter** - Search products by name/description and filter by category
- 📊 **Statistics Dashboard** - View total products, items in stock, and inventory value
- 🎨 **Modern UI** - Clean, responsive design with gradient backgrounds and smooth animations

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (local database)
- **ORM**: Flask-SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **UI Framework**: Bootstrap 5
- **Icons**: Bootstrap Icons

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jukkatv/InventoryApp.git
cd InventoryApp
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. The application will automatically create and populate the database with 20 sample products on first run.

## Database

The application uses SQLite as its database, which is stored in `inventory.db` (created automatically on first run). The database includes:

- **Products Table**: Stores product information including:
  - ID (Primary Key)
  - Name
  - Description
  - Quantity
  - Price
  - Category
  - Created At (timestamp)

### Pre-populated Products

The database comes with 20 sample products across various categories:
- Electronics (laptops, monitors, keyboards, etc.)
- Accessories (cables, stands, power banks, etc.)
- Office supplies (desk lamps, whiteboards, organizers, etc.)
- Furniture (chairs, desks, etc.)
- Stationery (notebooks, pens, etc.)
- Storage (SSDs, etc.)

## API Endpoints

### Get All Products
```
GET /api/products
```
Returns a JSON array of all products.

### Add Product
```
POST /api/products
Content-Type: application/json

{
  "name": "Product Name",
  "description": "Product Description",
  "price": 99.99,
  "quantity": 10,
  "category": "Electronics"
}
```

### Update Product Quantity
```
PUT /api/products/<product_id>
Content-Type: application/json

{
  "quantity": 15
}
```

### Delete Product
```
DELETE /api/products/<product_id>
```

## Project Structure

```
InventoryApp/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Frontend UI
├── inventory.db           # SQLite database (created automatically)
└── README.md              # This file
```

## Features in Detail

### Product Management
- **Add**: Click the "Add Product" button to open a modal form where you can enter product details
- **Update**: Use the +/- buttons or directly type in the quantity field to update stock levels
- **Delete**: Click the delete button and confirm to remove a product

### Search & Filtering
- **Search**: Type in the search box to filter products by name or description
- **Category Filter**: Select a category from the dropdown to show only products in that category
- **Sort**: Sort products by name, price (low to high or high to low), or quantity

### Statistics
The dashboard shows real-time statistics:
- Total number of unique products
- Total items in stock across all products
- Total inventory value (quantity × price for all products)

## Security

- Input validation on both frontend and backend
- SQL injection protection through SQLAlchemy ORM
- XSS prevention with proper HTML escaping
- CSRF protection can be added with Flask-WTF if needed

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.