from init import db, ma
from marshmallow import fields 

# {"id": 1, "message": "Comment 1", "user": {"id": 1, "name": "User 1", "email": etc...}, "card"" {"id": 1, "title": "Card 1", "comments": "blah blah" etc}"}
class Comment(db.Model): 
    __tablename__ = "comments"
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)

    user = db.relationship('User', back_populates='comments')
    card = db.relationship('Card', back_populates='comments')

# Converts the MODEL into something that json serialisable 
class CommentSchema(ma.Schema):
    # Singular, comment can only belong to one user or one card
    # Because user is a relationship, convert the user field according to the UserSchema.
    user = fields.Nested('UserSchema', only=['name', 'email'])
    card = fields.Nested('CardSchema', exclude=['comments'])

    class Meta:
        fields = ['id', 'message', 'card', 'user']

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
