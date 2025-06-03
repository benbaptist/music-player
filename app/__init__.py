from flask import Flask
from app.utils.data_service import data_service
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config')
    
    # Initialize Storify data service
    # This will create the data directory and initialize databases
    data_service.storify  # Access to initialize
    
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
    
    # Register cleanup handler
    @app.teardown_appcontext
    def close_data_service(error):
        data_service.flush_all()
    
    return app 