from src.models.user import db
from datetime import datetime
import json

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    merchant = db.Column(db.String(100), nullable=False)
    affiliate_link = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    features = db.Column(db.Text)  # JSON string for feature list
    in_stock = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'original_price': self.original_price,
            'merchant': self.merchant,
            'affiliate_link': self.affiliate_link,
            'image_url': self.image_url,
            'rating': self.rating,
            'review_count': self.review_count,
            'features': json.loads(self.features) if self.features else [],
            'in_stock': self.in_stock,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AffiliateClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.Text)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'clicked_at': self.clicked_at.isoformat()
        }

class ProductRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    suggestion_id = db.Column(db.Integer, db.ForeignKey('organization_suggestion.id'), nullable=True)
    relevance_score = db.Column(db.Float, default=0.0)
    reason = db.Column(db.Text)  # Why this product is recommended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'product_id': self.product_id,
            'suggestion_id': self.suggestion_id,
            'relevance_score': self.relevance_score,
            'reason': self.reason,
            'created_at': self.created_at.isoformat()
        }

