from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.room import Room, RoomItem, OrganizationSuggestion
import json

room_bp = Blueprint('room', __name__)

@room_bp.route('/rooms', methods=['GET'])
def get_rooms():
    """Get all rooms for a user"""
    user_id = request.args.get('user_id', 1)  # Default to user 1 for demo
    rooms = Room.query.filter_by(user_id=user_id).all()
    return jsonify([room.to_dict() for room in rooms])

@room_bp.route('/rooms', methods=['POST'])
def create_room():
    """Create a new room from scan data"""
    data = request.get_json()
    
    try:
        room = Room(
            name=data.get('name', 'Untitled Room'),
            user_id=data.get('user_id', 1),
            dimensions=json.dumps(data.get('dimensions', {})),
            scan_data=json.dumps(data.get('scan_data', {}))
        )
        
        db.session.add(room)
        db.session.flush()  # Get the room ID
        
        # Add room items
        items_data = data.get('items', [])
        for item_data in items_data:
            item = RoomItem(
                room_id=room.id,
                name=item_data.get('name'),
                category=item_data.get('category'),
                position=json.dumps(item_data.get('position', {})),
                confidence=item_data.get('confidence', 0.0)
            )
            db.session.add(item)
        
        # Generate organization suggestions
        suggestions = generate_organization_suggestions(room.id, items_data)
        for suggestion_data in suggestions:
            suggestion = OrganizationSuggestion(
                room_id=room.id,
                suggestion_type=suggestion_data['type'],
                title=suggestion_data['title'],
                description=suggestion_data['description'],
                priority=suggestion_data['priority']
            )
            db.session.add(suggestion)
        
        db.session.commit()
        return jsonify(room.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@room_bp.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """Get a specific room with all details"""
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict())

@room_bp.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """Update room details"""
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    
    try:
        if 'name' in data:
            room.name = data['name']
        if 'dimensions' in data:
            room.dimensions = json.dumps(data['dimensions'])
        if 'scan_data' in data:
            room.scan_data = json.dumps(data['scan_data'])
        
        db.session.commit()
        return jsonify(room.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@room_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """Delete a room and all associated data"""
    room = Room.query.get_or_404(room_id)
    
    try:
        db.session.delete(room)
        db.session.commit()
        return jsonify({'message': 'Room deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@room_bp.route('/rooms/<int:room_id>/suggestions', methods=['GET'])
def get_room_suggestions(room_id):
    """Get organization suggestions for a room"""
    suggestions = OrganizationSuggestion.query.filter_by(room_id=room_id).order_by(OrganizationSuggestion.priority).all()
    return jsonify([suggestion.to_dict() for suggestion in suggestions])

@room_bp.route('/rooms/<int:room_id>/suggestions/<int:suggestion_id>/implement', methods=['POST'])
def implement_suggestion(room_id, suggestion_id):
    """Mark a suggestion as implemented"""
    suggestion = OrganizationSuggestion.query.filter_by(id=suggestion_id, room_id=room_id).first_or_404()
    
    try:
        suggestion.is_implemented = True
        db.session.commit()
        return jsonify(suggestion.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def generate_organization_suggestions(room_id, items):
    """Generate AI-powered organization suggestions based on room items"""
    suggestions = []
    
    # Analyze items by category
    categories = {}
    for item in items:
        category = item.get('category', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # Storage suggestions
    if len(items) > 3:
        suggestions.append({
            'type': 'storage',
            'title': 'Add storage bins for loose items',
            'description': 'This will help reduce clutter and make items easier to find',
            'priority': 1
        })
    
    # Furniture suggestions
    if 'storage' not in categories or len(categories.get('storage', [])) < 2:
        suggestions.append({
            'type': 'furniture',
            'title': 'Consider a bookshelf for better organization',
            'description': 'Vertical storage maximizes space efficiency',
            'priority': 2
        })
    
    # Organization suggestions
    if 'furniture' in categories and len(categories['furniture']) > 2:
        suggestions.append({
            'type': 'organization',
            'title': 'Use drawer organizers for small items',
            'description': 'Keep frequently used items easily accessible',
            'priority': 2
        })
    
    # Lighting suggestions
    if 'lighting' not in categories:
        suggestions.append({
            'type': 'lighting',
            'title': 'Improve lighting for better visibility',
            'description': 'Good lighting makes organization and daily tasks easier',
            'priority': 3
        })
    
    return suggestions

