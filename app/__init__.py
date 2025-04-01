from flask import Flask
from app.utils.models import db
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config')
    
    # Set up database
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE_URI', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Register blueprints
    from app.controllers.main import main_bp
    from app.controllers.player import player_bp
    from app.controllers.playlists import playlists_bp
    from app.controllers.files import files_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(player_bp, url_prefix='/player')
    app.register_blueprint(playlists_bp, url_prefix='/playlists')
    app.register_blueprint(files_bp, url_prefix='/files')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 