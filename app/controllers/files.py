from flask import Blueprint, jsonify, request
from app.utils import filesystem, audtool

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
    """Play a specific file."""
    data = request.get_json()
    file_path = data.get('path')
    
    if not file_path:
        return jsonify({
            'success': False,
            'error': 'Missing path parameter'
        }), 400
    
    # Clear current playlist and add the new file
    audtool.clear_playlist()
    audtool.add_song(f"file://{file_path}")
    audtool.play()
    
    return jsonify({'success': True})

@files_bp.route('/add-to-playlist', methods=['POST'])
def add_to_playlist():
    """Add a file to the current playlist."""
    data = request.get_json()
    file_path = data.get('path')
    
    if not file_path:
        return jsonify({
            'success': False,
            'error': 'Missing path parameter'
        }), 400
    
    audtool.add_song(f"file://{file_path}")
    return jsonify({'success': True}) 