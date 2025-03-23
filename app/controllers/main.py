from flask import Blueprint, render_template, jsonify
from app.utils import audtool

main_bp = Blueprint('main', __name__)

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
        
        return jsonify({
            'success': True,
            'status': status,
            'current_song': current_song,
            'volume': volume,
            'position': position,
            'playlist_length': playlist_length,
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