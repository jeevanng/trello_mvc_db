from flask import Blueprint, request
from init import db
from models.card import Card
from models.comment import Comment, comment_schema, comments_schema
from flask_jwt_extended import get_jwt_identity, jwt_required


comments_bp = Blueprint('comments', __name__, url_prefix='<int:card_id>/comments')

# cards/card_id/comments - POST (We know which comment that is meant for which card and ID)
# That's why we will post the blueprint in the card controller

# WE DON'T NEED FULL CRUD FOR EVERY MODEL. We usually read a comment when viewing the card. It does not need individual C"R"UD
@comments_bp.route('/', methods=['POST']) 
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
@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
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

@comments_bp.route('/<int:comment_id>', methods=['PUT', 'PATCH'])
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
