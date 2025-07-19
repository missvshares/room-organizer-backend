from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.product import Product, AffiliateClick, ProductRecommendation
from src.models.room import Room, OrganizationSuggestion
import json

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    """Get products with optional filtering"""
    category = request.args.get('category')
    room_id = request.args.get('room_id')
    limit = request.args.get('limit', 20, type=int)
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    products = query.limit(limit).all()
    
    # If room_id is provided, get personalized recommendations
    if room_id:
        recommendations = get_room_recommendations(room_id)
        # Merge with general products, prioritizing recommendations
        recommended_ids = [r['product_id'] for r in recommendations]
        recommended_products = [p for p in products if p.id in recommended_ids]
        other_products = [p for p in products if p.id not in recommended_ids]
        products = recommended_products + other_products[:limit-len(recommended_products)]
    
    return jsonify([product.to_dict() for product in products])

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@product_bp.route('/products/<int:product_id>/click', methods=['POST'])
def track_affiliate_click(product_id):
    """Track affiliate link clicks for analytics and commission"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    
    try:
        click = AffiliateClick(
            product_id=product_id,
            user_id=data.get('user_id'),
            room_id=data.get('room_id'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            referrer=request.headers.get('Referer')
        )
        
        db.session.add(click)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'affiliate_link': product.affiliate_link,
            'click_id': click.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@product_bp.route('/rooms/<int:room_id>/recommendations', methods=['GET'])
def get_room_product_recommendations(room_id):
    """Get product recommendations for a specific room"""
    room = Room.query.get_or_404(room_id)
    recommendations = get_room_recommendations(room_id)
    
    # Get the actual product data
    product_ids = [r['product_id'] for r in recommendations]
    products = Product.query.filter(Product.id.in_(product_ids), Product.is_active==True).all()
    
    # Combine product data with recommendation data
    result = []
    for product in products:
        recommendation = next((r for r in recommendations if r['product_id'] == product.id), None)
        product_data = product.to_dict()
        if recommendation:
            product_data['recommendation'] = {
                'relevance_score': recommendation['relevance_score'],
                'reason': recommendation['reason']
            }
        result.append(product_data)
    
    # Sort by relevance score
    result.sort(key=lambda x: x.get('recommendation', {}).get('relevance_score', 0), reverse=True)
    
    return jsonify(result)

@product_bp.route('/analytics/clicks', methods=['GET'])
def get_click_analytics():
    """Get affiliate click analytics"""
    days = request.args.get('days', 30, type=int)
    
    # This would typically include more sophisticated analytics
    # For now, return basic click counts
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    clicks = db.session.query(
        Product.name,
        Product.merchant,
        func.count(AffiliateClick.id).label('click_count')
    ).join(AffiliateClick).filter(
        AffiliateClick.clicked_at >= start_date
    ).group_by(Product.id).all()
    
    return jsonify([{
        'product_name': click.name,
        'merchant': click.merchant,
        'click_count': click.click_count
    } for click in clicks])

def get_room_recommendations(room_id):
    """Generate product recommendations based on room analysis"""
    room = Room.query.get(room_id)
    if not room:
        return []
    
    suggestions = OrganizationSuggestion.query.filter_by(room_id=room_id).all()
    
    recommendations = []
    
    for suggestion in suggestions:
        # Map suggestion types to product categories
        if suggestion.suggestion_type == 'storage':
            products = Product.query.filter_by(category='storage', is_active=True).limit(3).all()
            for product in products:
                recommendations.append({
                    'product_id': product.id,
                    'relevance_score': 0.9 if suggestion.priority == 1 else 0.7,
                    'reason': f"Recommended for: {suggestion.title}"
                })
        
        elif suggestion.suggestion_type == 'furniture':
            products = Product.query.filter_by(category='furniture', is_active=True).limit(2).all()
            for product in products:
                recommendations.append({
                    'product_id': product.id,
                    'relevance_score': 0.8 if suggestion.priority == 1 else 0.6,
                    'reason': f"Recommended for: {suggestion.title}"
                })
    
    # Add some general recommendations
    general_products = Product.query.filter_by(is_active=True).limit(2).all()
    for product in general_products:
        if not any(r['product_id'] == product.id for r in recommendations):
            recommendations.append({
                'product_id': product.id,
                'relevance_score': 0.5,
                'reason': "Popular organization solution"
            })
    
    return recommendations

# Initialize some sample products
@product_bp.route('/products/seed', methods=['POST'])
def seed_products():
    """Seed the database with sample products (for development)"""
    sample_products = [
        {
            'name': 'IKEA ALGOT Storage System',
            'description': 'Modular storage system perfect for organizing any room',
            'category': 'storage',
            'price': 89.99,
            'original_price': 109.99,
            'merchant': 'IKEA',
            'affiliate_link': 'https://www.ikea.com/us/en/p/algot-shelf-unit-white-s49022093/?affiliate=roomscan',
            'rating': 4.5,
            'review_count': 1247,
            'features': json.dumps(['Adjustable shelves', 'Easy assembly', 'Durable metal construction'])
        },
        {
            'name': 'Container Store Elfa Shelving',
            'description': 'Premium modular shelving system for maximum organization',
            'category': 'storage',
            'price': 159.99,
            'original_price': 199.99,
            'merchant': 'The Container Store',
            'affiliate_link': 'https://www.containerstore.com/s/elfa/elfa-shelving?affiliate=roomscan',
            'rating': 4.8,
            'review_count': 892,
            'features': json.dumps(['Lifetime warranty', 'Custom configurations', 'Professional installation'])
        },
        {
            'name': 'Wayfair Storage Ottoman',
            'description': 'Multi-functional ottoman with hidden storage compartment',
            'category': 'furniture',
            'price': 79.99,
            'original_price': 99.99,
            'merchant': 'Wayfair',
            'affiliate_link': 'https://www.wayfair.com/furniture/pdp/storage-ottoman?affiliate=roomscan',
            'rating': 4.3,
            'review_count': 2156,
            'features': json.dumps(['Hidden storage', 'Comfortable seating', 'Multiple colors available'])
        },
        {
            'name': 'Amazon Basics Storage Bins',
            'description': 'Set of 6 collapsible fabric storage bins with handles',
            'category': 'storage',
            'price': 24.99,
            'original_price': 34.99,
            'merchant': 'Amazon',
            'affiliate_link': 'https://amazon.com/dp/B07EXAMPLE?tag=roomscan-20',
            'rating': 4.2,
            'review_count': 5432,
            'features': json.dumps(['Collapsible design', 'Reinforced handles', 'Machine washable'])
        }
    ]
    
    try:
        for product_data in sample_products:
            # Check if product already exists
            existing = Product.query.filter_by(name=product_data['name']).first()
            if not existing:
                product = Product(**product_data)
                db.session.add(product)
        
        db.session.commit()
        return jsonify({'message': 'Products seeded successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

