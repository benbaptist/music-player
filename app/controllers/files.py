from flask import Blueprint, jsonify, request
from app.utils import filesystem, audtool
from app.utils.playlist_service import PlaylistService

files_bp = Blueprint('files', __name__)

@files_bp.route('/browse', methods=['GET'])
def browse():
    """Browse files in the configured directory."""
    directory = request.args.get('directory')
    contents = filesystem.get_directory_contents(directory)
    
    return jsonify({
        'success': True,
        'directory': contents
    })

@files_bp.route('/play', methods=['POST'])
def play_file():
    """Play a specific file through Audacious."""
    data = request.get_json()
    file_path = data.get('path')
    
    if not file_path:
        return jsonify({
            'success': False,
            'error': 'Missing path parameter'
        }), 400
    
    # Clear current playlist and add the new file
    audtool.clear_playlist()
    audtool.add_song(file_path)
    audtool.play()
    
    return jsonify({'success': True})

@files_bp.route('/add-to-playlist/<int:playlist_id>', methods=['POST'])
def add_to_playlist(playlist_id):
    """Add a file to a specific playlist."""
    data = request.get_json()
    file_path = data.get('path')
    
    if not file_path:
        return jsonify({
            'success': False,
            'error': 'Missing path parameter'
        }), 400
    
    track = PlaylistService.add_track_to_playlist(playlist_id, file_path)
    
    if not track:
        return jsonify({
            'success': False,
            'error': f'Failed to add track to playlist {playlist_id}'
        }), 500
    
    return jsonify({
        'success': True,
        'track': track.to_dict()
    })

@files_bp.route('/add-directory-to-playlist/<int:playlist_id>', methods=['POST'])
def add_directory_to_playlist(playlist_id):
    """Add all audio files in a directory to a playlist."""
    data = request.get_json()
    directory_path = data.get('path')
    recursive = data.get('recursive', True)
    
    if not directory_path:
        return jsonify({
            'success': False,
            'error': 'Missing path parameter'
        }), 400
    
    # Add as a watch path with auto_add=True to scan and add files
    watch_path = PlaylistService.add_watch_path(
        playlist_id=playlist_id, 
        path=directory_path, 
        recursive=recursive, 
        auto_add=True
    )
    
    if not watch_path:
        return jsonify({
            'success': False,
            'error': f'Failed to add directory to playlist {playlist_id}'
        }), 500
    
    return jsonify({
        'success': True,
        'watch_path': watch_path.to_dict()
    }) 