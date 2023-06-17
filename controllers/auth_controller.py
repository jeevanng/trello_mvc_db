from flask import Blueprint, request 
from init import db, bcrypt
from models.user import User, user_schema, users_schema
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def auth_register():
    try:
        # Using request.get_json(), we get the info from the postman body 
        # {
        # "name": "User 2",
        # "email": "user2@email.com",
        # "password": "123456"
        # }
        # The info above will now be in body_data variable 
        body_data = request.get_json()

        # Now with the info we grabbed, we need to actually create the new user with our models 
        # Create a new User Model instance from the user info 
        user = User()
        user.name = body_data.get('name')
        user.email = body_data.get('email')
        if body_data.get('password'):
            user.password = bcrypt.generate_password_hash(body_data.get('password')).decode('utf-8')
        # Add user to session 
        db.session.add(user)
        # Commit user to database
        db.session.commit()
        # Respond to the client 
        return user_schema.dump(user), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return { 'error': 'Email address already in use' }, 409
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return { 'error': f'The {err.orig.diag.column_name} is required' }, 409


    