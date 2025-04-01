from flask import Blueprint, render_template, jsonify, current_app
from app.utils import audtool
from app.utils.playlist_service import PlaylistService
from app.utils.models import Playlist, db

main_bp = Blueprint('main', __name__)

@main_bp.before_app_first_request
def init_app():
    """Initialize the application on first request."""
    try:
        # Clear all Audacious playlists on startup
        num_playlists = audtool.get_number_of_playlists()
        if num_playlists:
            for i in range(int(num_playlists)):
                audtool.set_current_playlist(0)
                audtool.clear_playlist()
        
        # Check if we need to migrate playlists from Audacious
        if int(num_playlists or 0) > 0 and Playlist.query.count() == 0:
            current_app.logger.info("Migrating playlists from Audacious...")
            PlaylistService.migrate_audacious_playlists()
        
        # Create a default playlist if none exists
        if Playlist.query.count() == 0:
            current_app.logger.info("Creating default playlist...")
            PlaylistService.create_playlist("Default")
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
        current_song = audtool.get_current_song_info()
        status = audtool.get_playback_status()
        volume = audtool.get_volume()
        position = audtool.get_playlist_position()
        playlist_length = audtool.get_playlist_length()
        
        # Get settings
        repeat = audtool.get_repeat_status()
        shuffle = audtool.get_shuffle_status()
        stop_after = audtool.get_stop_after_status()
        auto_advance = audtool.get_auto_advance_status()
        
        # Get all playlists from our database
        playlists = [p.to_dict() for p in PlaylistService.get_all_playlists()]
        
        # Try to find the track in our database
        track_id = None
        if current_song.get('filename'):
            from app.utils.models import Track
            track = Track.query.filter_by(filename=current_song['filename']).first()
            if track:
                track_id = track.id
        
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