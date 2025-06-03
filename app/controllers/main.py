from flask import Blueprint, render_template, jsonify, current_app
from app.utils import audtool
from app.utils.playlist_service import PlaylistService
from app.utils.data_service import data_service

main_bp = Blueprint('main', __name__)

@main_bp.before_app_first_request
def init_app():
    """Initialize the application on first request."""
    try:
        # Always maintain a clean slate in Audacious
        # We'll use it only as a player, not for playlist management
        audtool.clear_playlist()
        
        # Option to migrate Audacious playlists is available via the API
        # instead of doing it automatically here
        
        # Create a default playlist if none exists in our database
        playlists = PlaylistService.get_all_playlists()
        if len(playlists) == 0:
            current_app.logger.info("Creating default playlist...")
            default_playlist = PlaylistService.create_playlist("Default")
            PlaylistService.set_current_playlist(default_playlist.id)
    except Exception as e:
        current_app.logger.error(f"Error initializing app: {e}")

@main_bp.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@main_bp.route('/status')
def status():
    """Get the current player status for the UI."""
    try:
        # Get playback status and song info with fallbacks for errors
        try:
            current_song = audtool.get_current_song_info()
        except Exception as e:
            current_app.logger.error(f"Error getting current song info: {str(e)}")
            current_song = {
                'title': None, 'artist': None, 'album': None, 'length': None,
                'length_seconds': 0, 'position': None, 'position_seconds': 0, 
                'bitrate': None, 'filename': None
            }
            
        try:
            status = audtool.get_playback_status()
        except Exception:
            status = 'stopped'
            
        try:
            volume = audtool.get_volume()
            if volume is None:
                volume = 50  # Default volume
        except Exception:
            volume = 50  # Default volume
            
        try:
            position = audtool.get_playlist_position()
            if position is None:
                position = 0
        except Exception:
            position = 0
            
        try:
            playlist_length = audtool.get_playlist_length()
            if playlist_length is None or playlist_length == '0':
                playlist_length = 0
        except Exception:
            playlist_length = 0
        
        # Get settings with fallbacks for errors
        try:
            repeat = audtool.get_repeat_status()
        except Exception:
            repeat = 'off'
            
        try:
            shuffle = audtool.get_shuffle_status()
        except Exception:
            shuffle = 'off'
            
        try:
            stop_after = audtool.get_stop_after_status()
        except Exception:
            stop_after = 'off'
            
        try:
            auto_advance = audtool.get_auto_advance_status()
        except Exception:
            auto_advance = 'on'
        
        # Get all playlists from our database
        playlists = [p.to_dict() for p in PlaylistService.get_all_playlists()]
        
        # Try to find the track in our database
        track_id = None
        if current_song.get('filename'):
            tracks_db = data_service.get_tracks_db()
            for track in tracks_db.data.values():
                if hasattr(track, 'filename') and track.filename == current_song['filename']:
                    track_id = track.id
                    break
        
        return jsonify({
            'success': True,
            'status': status,
            'current_song': current_song,
            'track_id': track_id,
            'volume': volume,
            'position': position,
            'playlist_length': playlist_length,
            'playlists': playlists,
            'settings': {
                'repeat': repeat == 'on',
                'shuffle': shuffle == 'on',
                'stop_after': stop_after == 'on',
                'auto_advance': auto_advance == 'on'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 