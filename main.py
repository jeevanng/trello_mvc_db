from flask import Flask 
from init import db, ma, bcrypt, jwt 
# import the blueprint from controller to use flask db command
from controllers.cli_controller import db_commands
from controllers.auth_controller import auth_bp
from controllers.card_controller import cards_bp
import os 
from marshmallow.exceptions import ValidationError

def create_app():
    app = Flask(__name__)

    # Make it that flask json does not sort keys automatically, so we maintain the ordered we state in models.
    app.json.sort_keys = False

    #                                          dbms      driver      user      pw            port    db_name
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATABASE_URL")
    app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")

    # This will 
    @app.errorhandler(ValidationError)
    def validation_error(err):
        return {'error': err.messages}, 400

    @app.errorhandler(400)
    def bad_request(err):
        return {'error': str(err)}, 400
    
    @app.errorhandler(404)
    def not_found(err):
        return {'error': str(err)}, 404
    
    
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # register the blueprint db_commands
    app.register_blueprint(db_commands)
    # register auth_bp/cards blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(cards_bp)

    return app 

    

