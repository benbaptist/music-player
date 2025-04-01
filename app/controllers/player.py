from flask import Blueprint, jsonify, request
from app.utils import audtool
from app.utils.models import Track, db

player_bp = Blueprint('player', __name__)

@player_bp.route('/status', methods=['GET'])
def get_status():
    """Get the current playback status and song information."""
    status = audtool.get_playback_status()
    song_info = audtool.get_current_song_info()
    
    # Try to find the track in our database by filename
    track = None
    if song_info.get('filename'):
        track = Track.query.filter_by(filename=song_info['filename']).first()
    
    return jsonify({
        'success': True,
        'status': status,
        'song': song_info,
        'track_id': track.id if track else None
    })

@player_bp.route('/play', methods=['POST'])
def play():
    """Start or resume playback."""
    audtool.play()
    return jsonify({'success': True})

@player_bp.route('/pause', methods=['POST'])
def pause():
    """Pause playback."""
    audtool.pause()
    return jsonify({'success': True})

@player_bp.route('/playpause', methods=['POST'])
def playpause():
    """Toggle between play and pause."""
    audtool.playpause()
    return jsonify({'success': True})

@player_bp.route('/stop', methods=['POST'])
def stop():
    """Stop playback."""
    audtool.stop()
    return jsonify({'success': True})

@player_bp.route('/next', methods=['POST'])
def next_song():
    """Skip to the next song."""
    audtool.next_song()
    return jsonify({'success': True})

@player_bp.route('/previous', methods=['POST'])
def previous_song():
    """Skip to the previous song."""
    audtool.previous_song()
    return jsonify({'success': True})

@player_bp.route('/seek', methods=['POST'])
def seek():
    """Seek to a position in the current song."""
    data = request.get_json()
    position = data.get('position')
    
    if position is None:
        return jsonify({
            'success': False,
            'error': 'Missing position parameter'
        }), 400
    
    audtool.seek(position)
    return jsonify({'success': True})

@player_bp.route('/seek-relative', methods=['POST'])
def seek_relative():
    """Seek relative to the current position."""
    data = request.get_json()
    offset = data.get('offset')
    
    if offset is None:
        return jsonify({
            'success': False,
            'error': 'Missing offset parameter'
        }), 400
    
    audtool.seek_relative(offset)
    return jsonify({'success': True})

@player_bp.route('/volume', methods=['GET'])
def get_volume():
    """Get the current volume level."""
    volume = audtool.get_volume()
    return jsonify({
        'success': True,
        'volume': volume
    })

@player_bp.route('/volume', methods=['POST'])
def set_volume():
    """Set the volume level."""
    data = request.get_json()
    volume = data.get('volume')
    
    if volume is None:
        return jsonify({
            'success': False,
            'error': 'Missing volume parameter'
        }), 400
    
    # Ensure volume is in valid range
    try:
        volume = max(0, min(100, int(volume)))
        audtool.set_volume(volume)
        return jsonify({'success': True})
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Volume must be an integer between 0 and 100'
        }), 400

@player_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get current player settings."""
    repeat = audtool.get_repeat_status()
    shuffle = audtool.get_shuffle_status()
    stop_after = audtool.get_stop_after_status()
    auto_advance = audtool.get_auto_advance_status()
    
    return jsonify({
        'success': True,
        'settings': {
            'repeat': repeat == 'on',
            'shuffle': shuffle == 'on',
            'stop_after': stop_after == 'on',
            'auto_advance': auto_advance == 'on'
        }
    })

@player_bp.route('/settings/toggle-repeat', methods=['POST'])
def toggle_repeat():
    """Toggle repeat setting."""
    audtool.toggle_repeat()
    return jsonify({'success': True})

@player_bp.route('/settings/toggle-shuffle', methods=['POST'])
def toggle_shuffle():
    """Toggle shuffle setting."""
    audtool.toggle_shuffle()
    return jsonify({'success': True})

@player_bp.route('/settings/toggle-stop-after', methods=['POST'])
def toggle_stop_after():
    """Toggle stop after current song."""
    audtool.toggle_stop_after()
    return jsonify({'success': True})

@player_bp.route('/settings/toggle-auto-advance', methods=['POST'])
def toggle_auto_advance():
    """Toggle auto advance setting."""
    audtool.toggle_auto_advance()
    return jsonify({'success': True})

@player_bp.route('/clear', methods=['POST'])
def clear_audacious():
    """Clear the Audacious playlist (to maintain clean slate)."""
    audtool.clear_playlist()
    return jsonify({'success': True}) 