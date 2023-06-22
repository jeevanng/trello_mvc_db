from flask import Flask 
from init import db, ma, bcrypt, jwt 
# import the blueprint from controller to use flask db command
from controllers.cli_controller import db_commands
from controllers.auth_controller import auth_bp
from controllers.card_controller import cards_bp
import os 

def create_app():
    app = Flask(__name__)
    #                                          dbms      driver      user      pw            port    db_name
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATABASE_URL")
    app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")

    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # register the blueprint db_commands
    app.register_blueprint(db_commands)
    # register auth_bp blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(cards_bp)

    return app 

    

