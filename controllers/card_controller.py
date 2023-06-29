from flask import Blueprint, request
from init import db
from models.card import Card, cards_schema, card_schema
from models.comment import Comment, comment_schema, comments_schema 
from datetime import date
from flask_jwt_extended import get_jwt_identity, jwt_required


cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

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
    body_data = request.get_json()
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
    body_data = request.get_json()
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
    
# cards/card_id/comments - POST (We know which comment that is meant for which card and ID)
# That's why we will post the blueprint in the card controller

# WE DON'T NEED FULL CRUD FOR EVERY MODEL. We usually read a comment when viewing the card. It does not need individual C"R"UD
@cards_bp.route('/<int:card_id>/comments', methods=['POST']) 
@jwt_required()
def create_comment(card_id):
    body_data = request.get_json()
    # SELECT * FROM card WHERE id=card_id
    stmt = db.select(Card).filter_by(id=card_id) 
    # This card variable below is in an instance of the model 
    card = db.session.scalar(stmt)
    
    if card: 
        # Import the comments model and schemas
        comment = Comment(
            message=body_data.get('message'),
            # pass id to the _id field
            user_id=get_jwt_identity(),
            # Single card by itself, in the def(). 
            card_id=card.id
            # card_id=card.id can also be written as card=card in this instance, this passes the model instance to the model field
        )

        db.session.add(comment)
        db.session.commit()
        return comment_schema.dump(comment), 201
    else:
        return {'error': f'Card not found with id {card_id}'}, 404

# Need to know which card id and comment id to delete
@cards_bp.route('/<int:card_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(card_id, comment_id):
    # If only the owner of the card can delete the card, then card_id will come into play. 
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)

    if comment:
        db.session.delete(comment)
        db.session.commit()
        return {'message': f'Comment {comment.message} deleted successfully'}
    else:
        return {'error': f'Comment with {comment_id} not found.'}, 404

@cards_bp.route('/<int:card_id>/comments/<int:comment_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_comment(card_id, comment_id):
    body_data = request.get_json()
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)

    if comment:
        # If the first part body_data.get('message') is true, it will not execute the comment.message, which is what we want
        # The first truth value will be passed, order matters here
        # If we do not get a message in the body_data, just pass the original message 
        comment.message = body_data.get('message') or comment.message
        db.session.commit()
        return comment_schema.dump(comment)
    else:
        return {'error': f'Comment with comment id {comment_id} does not exist.'}, 404
