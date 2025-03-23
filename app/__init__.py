from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config')
    
    # Register blueprints
    from app.controllers.main import main_bp
    from app.controllers.player import player_bp
    from app.controllers.playlists import playlists_bp
    from app.controllers.files import files_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(player_bp, url_prefix='/player')
    app.register_blueprint(playlists_bp, url_prefix='/playlists')
    app.register_blueprint(files_bp, url_prefix='/files')
    
    return app 