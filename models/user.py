from init import db, ma 
from marshmallow import fields
# import the db from the init file. db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Because a user can have zero or many cards, it will be plural. Not "card", singular
    cards = db.relationship('Card', back_populates='user', cascade='all, delete')

class UserSchema(ma.Schema):
    # Because this is multiple, we use .List
    # Plural here, because one user can have multiple/many cards
    cards = fields.List(fields.Nested('Cards', exclude=['user']))

    class Meta:
        # Whenever we dump, this is what we get
        fields = ('id', 'name', 'email', 'password', 'is_admin', 'cards')

user_schema = UserSchema(exclude=['password'])
users_schema = UserSchema(many=True, exclude=['password'])