from init import db, ma 
from marshmallow import fields 

class Card(db.Model):
    __tablename__ = "cards"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.Date) # Date created
    status = db.Column(db.String)
    priority = db.Column(db.String)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # The model () in relates to
    user = db.relationship('User', back_populates='cards')
    # {id:1, title: "Card 1", description: "ajsdlfjds", etc, user: {id: 3, name: "User 1", email: "User1@email.com" etc}}
    # Returns the information about the user which created the card 

class CardSchema(ma.Schema):
    user = fields.Nested('UserSchema', only=['name', 'email'])

    class Meta: 
        fields = ('id', 'title', 'description', 'date', 'status', 'priority', 'user')
        # When we dump data, the order of the fields will be followed 
        ordered = True 

card_schema = CardSchema()
cards_schema = CardSchema(many=True)