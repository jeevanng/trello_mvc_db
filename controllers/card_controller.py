from flask import Blueprint, request
from init import db
from models.card import Card, cards_schema, card_schema
from datetime import date
from flask_jwt_extended import get_jwt_identity, jwt_required
from controllers.comment_controller import comments_bp

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')
# Register blueprint in cards_bp
cards_bp.register_blueprint(comments_bp)
# So now the routes will be /cards/<int:card_id>/comments

@cards_bp.route('/')
def get_all_cards():
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return cards_schema.dump(cards)

@cards_bp.route('<int:id>')
def get_one_card(id):   
    # id column is equal to the id (listed in the route and variable)
    stmt = db.select(Card).filter_by(id=id)
    # Can also be written as below;
    # stmt = db.select(Card).where(Card.id==id)
    card = db.session.scalar(stmt)

    if card: 
        return card_schema.dump(card)
    else:
        return {'error': f'Card not found with id {id}'}, 404
    
@cards_bp.route('/', methods=['POST'])
@jwt_required()
def create_card():
    # .load will use the marshmallow validator now, the min=2 etc. 
    body_data = card_schema.load(request.get_json())
    # create new card model instance
    card = Card(
        title=body_data.get('title'),
        description=body_data.get('description'),
        date=date.today(),
        status=body_data.get('status'),
        priority=body_data.get('priority'),
        user_id=get_jwt_identity()
    )

    # Add that card to the session
    db.session.add(card)
    # Commit
    db.session.commit()

    # Respond to the client, singular card 
    return card_schema.dump(card), 201

@cards_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        db.session.delete(card)
        db.session.commit()
        return {'message': f'Card {card.title} was deleted successfully'}
    else:
        return {'error': f'Card not found with id {id}.'}, 404

# PUT and PATCH for editing resource. PUT try to edit the resource, if it doesn't exist it will also create, if we miss any fields,
# it will edit that back to null.

# If we use PATCH, only update the fields we pass (in postman), if we forget to pass, it will leave the fields as they were previously
# Will not create a new resource as well
@cards_bp.route('/<int:id>', methods=['PUT', 'PATCH'])
# Whether we use PUT or PATCH, we will still run through the function below
@jwt_required()
def update_one_card(id):
    body_data = card_schema.load(request.get_json(), partial=True)
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)

    if card:
        card.title = body_data.get('title') or card.title
        card.description = body_data.get('description') or card.description
        card.status = body_data.get('status') or card.status
        card.priority = body_data.get('priority') or card.priority 
        db.session.commit()
        return card_schema.dump(card)
    else:
        return {'error': f'Card not found with {id}'}, 404
    
