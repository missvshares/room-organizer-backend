import os
import sys

# Explicitly add the project root to sys.path (keep this for robustness)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, project_root)

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.admin import Admin
from src.models.analytics import UserActivity, AffiliateClick, RoomScan, AppMetrics
from src.models.product import Product
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.analytics import analytics_bp
from src.routes.products import products_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'roomscan-admin-secret-key-change-in-production'

# Enable CORS for all routes
CORS(app, resources={r'/api/*': {'origins': 'https://admin-dashboard-roomscan-victorias-projects-7fdc1e3e.vercel.app', 'supports_credentials': True}})
# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(products_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Create default admin user if none exists
    if not Admin.query.first():
        default_admin = Admin(
            username='admin',
            email='admin@roomscan.com',
            role='super_admin'
        )
        default_admin.set_password('admin123')  # Change this in production!
        db.session.add(default_admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='admin123'")

@app.route('/', defaults={'path': ''}) 
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)


