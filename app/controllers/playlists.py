from flask import Blueprint, jsonify, request
from app.utils import audtool
from app.utils.playlist_service import PlaylistService

playlists_bp = Blueprint('playlists', __name__)

@playlists_bp.route('/', methods=['GET'])
def get_playlists():
    """Get all available playlists."""
    try:
        playlists = PlaylistService.get_all_playlists()
        
        return jsonify({
            'success': True,
            'playlists': [p.to_dict() for p in playlists]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """Get information about a specific playlist."""
    try:
        playlist = PlaylistService.get_playlist(playlist_id)
        
        if not playlist:
            return jsonify({
                'success': False,
                'error': f'Playlist with ID {playlist_id} not found'
            }), 404
            
        tracks = PlaylistService.get_playlist_tracks(playlist_id)
        
        playlist_data = playlist.to_dict()
        playlist_data['tracks'] = [t.to_dict() for t in tracks]
        
        return jsonify({
            'success': True,
            'playlist': playlist_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/new', methods=['POST'])
def create_playlist():
    """Create a new playlist."""
    try:
        data = request.get_json()
        name = data.get('name', 'New Playlist')
        
        playlist = PlaylistService.create_playlist(name)
        
        return jsonify({
            'success': True,
            'playlist': playlist.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>/rename', methods=['POST'])
def rename_playlist(playlist_id):
    """Rename a playlist."""
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Missing name parameter'
            }), 400
            
        playlist = PlaylistService.rename_playlist(playlist_id, name)
        
        if not playlist:
            return jsonify({
                'success': False,
                'error': f'Playlist with ID {playlist_id} not found'
            }), 404
            
        return jsonify({
            'success': True,
            'playlist': playlist.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>/delete', methods=['POST'])
def delete_playlist(playlist_id):
    """Delete a playlist."""
    try:
        result = PlaylistService.delete_playlist(playlist_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Playlist with ID {playlist_id} not found'
            }), 404
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>/add', methods=['POST'])
def add_track(playlist_id):
    """Add a track to a playlist."""
    try:
        data = request.get_json()
        track_path = data.get('path')
        
        if not track_path:
            return jsonify({
                'success': False,
                'error': 'Missing path parameter'
            }), 400
            
        track = PlaylistService.add_track_to_playlist(playlist_id, track_path)
        
        if not track:
            return jsonify({
                'success': False,
                'error': f'Failed to add track to playlist {playlist_id}'
            }), 500
            
        return jsonify({
            'success': True,
            'track': track.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>/remove/<int:track_id>', methods=['POST'])
def remove_track(playlist_id, track_id):
    """Remove a track from a playlist."""
    try:
        result = PlaylistService.remove_track_from_playlist(playlist_id, track_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Failed to remove track {track_id} from playlist {playlist_id}'
            }), 404
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>/reorder', methods=['POST'])
def reorder_track(playlist_id):
    """Reorder a track within a playlist."""
    try:
        data = request.get_json()
        track_id = data.get('track_id')
        new_position = data.get('position')
        
        if track_id is None or new_position is None:
            return jsonify({
                'success': False,
                'error': 'Missing track_id or position parameter'
            }), 400
            
        result = PlaylistService.reorder_track(playlist_id, track_id, new_position)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Failed to reorder track {track_id} in playlist {playlist_id}'
            }), 404
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>/settings', methods=['POST'])
def update_settings(playlist_id):
    """Update playlist settings."""
    try:
        data = request.get_json()
        settings = data.get('settings', {})
        
        playlist = PlaylistService.update_playlist_settings(playlist_id, settings)
        
        if not playlist:
            return jsonify({
                'success': False,
                'error': f'Playlist with ID {playlist_id} not found'
            }), 404
            
        return jsonify({
            'success': True,
            'playlist': playlist.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>/play', methods=['POST'])
def play_playlist(playlist_id):
    """Load a playlist into Audacious and start playback."""
    try:
        # Load the playlist into Audacious
        PlaylistService.load_playlist_to_audacious(playlist_id)
        
        # Start playback
        audtool.play()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/migrate', methods=['POST'])
def migrate_playlists():
    """Migrate playlists from Audacious to the new system."""
    try:
        playlists = PlaylistService.migrate_audacious_playlists()
        
        # Clear all Audacious playlists 
        # (we'll use our new system from now on)
        num_playlists = audtool.get_number_of_playlists()
        if num_playlists:
            for i in range(int(num_playlists)):
                audtool.set_current_playlist(0)
                audtool.delete_current_playlist()
        
        return jsonify({
            'success': True,
            'message': f'Migrated {len(playlists)} playlists from Audacious'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Watchlist endpoints
@playlists_bp.route('/<int:playlist_id>/watchpaths', methods=['GET'])
def get_watch_paths(playlist_id):
    """Get all watch paths for a playlist."""
    try:
        playlist = PlaylistService.get_playlist(playlist_id)
        
        if not playlist:
            return jsonify({
                'success': False,
                'error': f'Playlist with ID {playlist_id} not found'
            }), 404
            
        return jsonify({
            'success': True,
            'watch_paths': [wp.to_dict() for wp in playlist.watch_paths]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/<int:playlist_id>/watchpaths/add', methods=['POST'])
def add_watch_path(playlist_id):
    """Add a watch path to a playlist."""
    try:
        data = request.get_json()
        path = data.get('path')
        recursive = data.get('recursive', True)
        auto_add = data.get('auto_add', True)
        
        if not path:
            return jsonify({
                'success': False,
                'error': 'Missing path parameter'
            }), 400
            
        watch_path = PlaylistService.add_watch_path(playlist_id, path, recursive, auto_add)
        
        if not watch_path:
            return jsonify({
                'success': False,
                'error': f'Failed to add watch path to playlist {playlist_id}'
            }), 500
            
        return jsonify({
            'success': True,
            'watch_path': watch_path.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/watchpaths/<int:watch_path_id>/remove', methods=['POST'])
def remove_watch_path(watch_path_id):
    """Remove a watch path."""
    try:
        result = PlaylistService.remove_watch_path(watch_path_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Watch path with ID {watch_path_id} not found'
            }), 404
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/watchpaths/<int:watch_path_id>/scan', methods=['POST'])
def scan_watch_path(watch_path_id):
    """Scan a watch path and add files to the playlist."""
    try:
        result = PlaylistService.scan_watch_path(watch_path_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Watch path with ID {watch_path_id} not found'
            }), 404
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 