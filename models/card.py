from init import db, ma 
from marshmallow import fields, validates
from marshmallow.validate import Length, And, Regexp, OneOf
from marshmallow.exceptions import ValidationError

VALID_STATUSES = ('To Do', 'Done', 'Ongoing', 'Testing', 'Deployed')
VALID_PRIORITIES = ('Low', 'Medium', 'High', 'Urgent')

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
    # The back_populates='cards' needs to match the 'cards' or variable name in user.py models and vice versa
    user = db.relationship('User', back_populates='cards')
    # {id:1, title: "Card 1", description: "ajsdlfjds", etc, user: {id: 3, name: "User 1", email: "User1@email.com" etc}}
    # Returns the information about the user which created the card 
    comments = db.relationship('Comment', back_populates='card', cascade='all, delete')

    # Relationship will not appear in the database under columns, however it will be extracted from ORM. SQLAlchemy 

class CardSchema(ma.Schema):
    # We use singular here, because one card can only have one user
    user = fields.Nested('UserSchema', only=['name', 'email'])
    comments = fields.List(fields.Nested('CommentSchema', exclude=['card']))

    # Using marshmallow validation
    # Sets minimum length of title, and also requires field to be not null
    title = fields.String(required=True, validate=And(
        Length(min=2, error='Title must be at least 2 characters long'),
        Regexp('^[a-zA-Z0-9 ]+$', error='Only letters, spaces and numbers are allowed')
    ))

    # Status must be equal to one of the elements in the VALID_STATUSES variable, indicated at the top
    status = fields.String(validate=OneOf(VALID_STATUSES))

    priority = fields.String(validate=OneOf(VALID_PRIORITIES))

    @validates('status')
    def validate_status(self, value):
        # What is the index of that validate status, we want 'Ongoing', at index 2 in VALIDATE_STATUSES
        # We use index, because if we directly type "Ongoing", if we change that word in the future we need to change it in too many places
        if value == VALID_STATUSES[2]:
            # count the rows of how many VALID_STATUSES[2] exist
            stmt = db.select(db.func.count()).select_from(Card).filter_by(status=VALID_STATUSES[2])
            count = db.session.scalar(stmt)
            # If there is an ongoing card or not
            # We only want one card to have 'Ongoing'
            if count > 0: 
                raise ValidationError('You already have an ongoing card')

    class Meta: 
        fields = ('id', 'title', 'description', 'date', 'status', 'priority', 'user', 'comments')
        # When we dump data, the order of the fields will be followed 
        ordered = True 

card_schema = CardSchema()
cards_schema = CardSchema(many=True)