from src.models.user import db
from datetime import datetime
import json

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dimensions = db.Column(db.Text)  # JSON string for width, height, length
    scan_data = db.Column(db.Text)  # JSON string for 3D scan data
    items = db.relationship('RoomItem', backref='room', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'dimensions': json.loads(self.dimensions) if self.dimensions else None,
            'scan_data': json.loads(self.scan_data) if self.scan_data else None,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RoomItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    position = db.Column(db.Text)  # JSON string for x, y, z coordinates
    confidence = db.Column(db.Float, default=0.0)  # AI detection confidence
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'name': self.name,
            'category': self.category,
            'position': json.loads(self.position) if self.position else None,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat()
        }

class OrganizationSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    suggestion_type = db.Column(db.String(50), nullable=False)  # 'storage', 'furniture', 'layout'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Integer, default=1)  # 1=high, 2=medium, 3=low
    is_implemented = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'suggestion_type': self.suggestion_type,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'is_implemented': self.is_implemented,
            'created_at': self.created_at.isoformat()
        }

