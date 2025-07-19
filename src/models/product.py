from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    merchant = db.Column(db.String(100))
    affiliate_link = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500))
    price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Product {self.name}>'

class AffiliateClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer) # Optional: if you track users
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

    product = db.relationship('Product', backref=db.backref('clicks', lazy=True))

    def __repr__(self):
        return f'<AffiliateClick {self.product.name} at {self.timestamp}>'


