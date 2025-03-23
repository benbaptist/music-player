from flask import Blueprint, jsonify, request
from app.utils import audtool

playlists_bp = Blueprint('playlists', __name__)

@playlists_bp.route('/', methods=['GET'])
def get_playlists():
    """Get all available playlists."""
    try:
        num_playlists = audtool.get_number_of_playlists()
        current_playlist = audtool.get_current_playlist()
        
        if not num_playlists:
            return jsonify({
                'success': False,
                'error': 'Failed to get number of playlists'
            }), 500
            
        num_playlists = int(num_playlists)
        playlists = []
        
        # Get all playlists and their names
        for i in range(num_playlists):
            # We need to set the current playlist to get its name
            current = audtool.set_current_playlist(i)
            playlist_name = audtool.get_current_playlist_name() or f"Playlist {i+1}"
            
            playlists.append({
                'id': i,
                'name': playlist_name,
                'is_current': str(i) == current_playlist
            })
            
        # Restore the original current playlist
        audtool.set_current_playlist(current_playlist)
            
        return jsonify({
            'success': True,
            'playlists': playlists,
            'current_playlist': current_playlist
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/current', methods=['GET'])
def get_current_playlist():
    """Get information about the current playlist."""
    try:
        current_id = audtool.get_current_playlist()
        name = audtool.get_current_playlist_name()
        songs = audtool.get_all_songs()
        current_position = audtool.get_playlist_position()
        
        return jsonify({
            'success': True,
            'id': current_id,
            'name': name,
            'songs': songs,
            'current_position': current_position
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/set-current/<int:playlist_id>', methods=['POST'])
def set_current_playlist(playlist_id):
    """Set the current playlist."""
    num_playlists = audtool.get_number_of_playlists()
    
    if not num_playlists:
        return jsonify({
            'success': False,
            'error': 'Failed to get number of playlists'
        }), 500
        
    if playlist_id < 0 or playlist_id >= int(num_playlists):
        return jsonify({
            'success': False,
            'error': f'Invalid playlist ID: {playlist_id}'
        }), 400
        
    audtool.set_current_playlist(playlist_id)
    return jsonify({'success': True})

@playlists_bp.route('/rename', methods=['POST'])
def rename_playlist():
    """Rename the current playlist."""
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({
            'success': False,
            'error': 'Missing name parameter'
        }), 400
        
    audtool.set_current_playlist_name(name)
    return jsonify({'success': True})

@playlists_bp.route('/new', methods=['POST'])
def create_playlist():
    """Create a new playlist."""
    audtool.new_playlist()
    
    data = request.get_json()
    name = data.get('name')
    
    if name:
        audtool.set_current_playlist_name(name)
        
    return jsonify({'success': True})

@playlists_bp.route('/delete', methods=['POST'])
def delete_playlist():
    """Delete the current playlist."""
    audtool.delete_current_playlist()
    return jsonify({'success': True})

@playlists_bp.route('/clear', methods=['POST'])
def clear_playlist():
    """Clear the current playlist."""
    audtool.clear_playlist()
    return jsonify({'success': True})

@playlists_bp.route('/add', methods=['POST'])
def add_song():
    """Add a song to the current playlist."""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({
            'success': False,
            'error': 'Missing url parameter'
        }), 400
        
    audtool.add_song(url)
    return jsonify({'success': True})

@playlists_bp.route('/delete-song/<int:position>', methods=['POST'])
def delete_song(position):
    """Delete a song from the current playlist."""
    audtool.delete_song(position)
    return jsonify({'success': True})

@playlists_bp.route('/jump/<int:position>', methods=['POST'])
def jump_to_song(position):
    """Jump to a specific song in the playlist."""
    audtool.jump_to_song(position)
    return jsonify({'success': True}) 