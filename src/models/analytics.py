from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer) # Optional: if you track users
    activity_type = db.Column(db.String(50), nullable=False) # 'room_scan', 'product_click', etc.
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    metadata = db.Column(db.JSON) # Store additional data as JSON

    def __repr__(self):
        return f'<UserActivity {self.activity_type} at {self.timestamp}>'

class AffiliateClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer) # Optional: if you track users
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    converted = db.Column(db.Boolean, default=False)
    commission_amount = db.Column(db.Float)

    def __repr__(self):
        return f'<AffiliateClick product_id={self.product_id} at {self.timestamp}>'

class RoomScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer) # Optional: if you track users
    room_type = db.Column(db.String(50)) # 'bedroom', 'kitchen', etc.
    scan_data = db.Column(db.JSON) # Store scan results as JSON
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    organization_suggestions = db.Column(db.JSON) # Store suggestions as JSON

    def __repr__(self):
        return f'<RoomScan {self.room_type} at {self.timestamp}>'

class AppMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    metadata = db.Column(db.JSON) # Store additional data as JSON

    def __repr__(self):
        return f'<AppMetrics {self.metric_name}={self.metric_value} at {self.timestamp}>'

