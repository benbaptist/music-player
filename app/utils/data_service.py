from storify import Storify
from app.utils.models import Playlist, Track, WatchPath
import os

class DataService:
    _instance = None
    _storify = None
    _databases = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._storify is None:
            # Initialize Storify with our models
            # Use config if available, otherwise default
            try:
                from flask import current_app
                data_dir = current_app.config.get('DATA_DIR', './data')
            except RuntimeError:
                # Outside of app context
                data_dir = os.path.join(os.getcwd(), 'data')
            
            os.makedirs(data_dir, exist_ok=True)
            
            self._storify = Storify(
                root=data_dir,
                models=[Playlist, Track, WatchPath],
                save_interval=60,  # Auto-save every minute
                verbose=True
            )
            
            # Initialize database cache
            self._databases = {}
    
    @property
    def storify(self):
        return self._storify
    
    def _get_cached_db(self, db_name):
        """Get a cached database instance."""
        if db_name not in self._databases:
            self._databases[db_name] = self._storify.get_db(db_name)
        return self._databases[db_name]
    
    def get_playlists_db(self):
        """Get the playlists database."""
        return self._get_cached_db("playlists")
    
    def get_tracks_db(self):
        """Get the tracks database."""
        return self._get_cached_db("tracks")
    
    def get_watch_paths_db(self):
        """Get the watch paths database."""
        return self._get_cached_db("watch_paths")
    
    def get_settings_db(self):
        """Get the settings database for app-wide settings."""
        return self._get_cached_db("settings")
    
    def flush_all(self):
        """Manually flush all databases."""
        self._storify.flush()
    
    def close(self):
        """Close all databases."""
        if self._storify:
            self._storify.flush()


# Global instance
data_service = DataService() 