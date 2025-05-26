from flask import Blueprint, jsonify, request
from app.utils import audtool
from app.utils.playlist_service import PlaylistService

playlists_bp = Blueprint('playlists', __name__)

@playlists_bp.route('/', methods=['GET'])
def get_playlists():
    """Get all available playlists."""
    try:
        playlists = PlaylistService.get_all_playlists()
        current_playlist = PlaylistService.get_current_playlist()
        current_playlist_id = current_playlist.id if current_playlist else None
        
        playlist_data = []
        for p in playlists:
            data = p.to_dict()
            data['is_current'] = (p.id == current_playlist_id)
            playlist_data.append(data)
        
        return jsonify({
            'success': True,
            'playlists': playlist_data,
            'current_playlist': current_playlist_id
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
        # First, ensure we have fully cleared Audacious
        audtool.clear_playlist()
        
        # Load the playlist into Audacious
        success = PlaylistService.load_playlist_to_audacious(playlist_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': f'Failed to load playlist {playlist_id}'
            }), 404
        
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

@playlists_bp.route('/current', methods=['GET'])
def get_current_playlist():
    """Get the current playlist for the UI."""
    try:
        current_playlist = PlaylistService.get_current_playlist()
        
        if not current_playlist:
            # If there's no current playlist, create a new one
            current_playlist = PlaylistService.create_playlist("New Playlist")
            PlaylistService.set_current_playlist(current_playlist.id)
            
            return jsonify({
                'success': True,
                'songs': [],
                'current_position': 0
            })
            
        tracks = PlaylistService.get_playlist_tracks(current_playlist.id)
        
        # Try to get the current position from Audacious if currently playing our playlist
        # This is optional since we're decoupling playlists from Audacious
        try:
            current_position = audtool.get_playlist_position()
            if current_position is None:
                current_position = 0
        except Exception:
            # If audtool command fails or Audacious isn't playing our playlist, default to 0
            current_position = 0
        
        return jsonify({
            'success': True,
            'songs': [t.to_dict() for t in tracks],
            'current_position': current_position
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/set-current/<int:playlist_id>', methods=['POST'])
def set_current_playlist(playlist_id):
    """Set the current active playlist."""
    try:
        playlist = PlaylistService.set_current_playlist(playlist_id)
        
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

@playlists_bp.route('/<int:playlist_id>/debug', methods=['GET'])
def debug_playlist(playlist_id):
    """Debug endpoint to show detailed playlist information."""
    try:
        playlist = PlaylistService.get_playlist(playlist_id)
        
        if not playlist:
            return jsonify({
                'success': False,
                'error': f'Playlist with ID {playlist_id} not found'
            }), 404
        
        # Get tracks using the proper method
        tracks = PlaylistService.get_playlist_tracks(playlist_id)
        
        # Get raw relationship data
        raw_tracks = playlist.tracks
        
        # Get association table data
        from app.utils.models import playlist_tracks, db
        association_data = db.session.query(playlist_tracks).filter(
            playlist_tracks.c.playlist_id == playlist_id
        ).order_by(playlist_tracks.c.position).all()
        
        debug_info = {
            'playlist_id': playlist_id,
            'playlist_name': playlist.name,
            'tracks_via_get_tracks': [
                {
                    'id': t.id,
                    'title': t.title,
                    'filename': t.filename,
                    'position': i
                } for i, t in enumerate(tracks)
            ],
            'tracks_via_relationship': [
                {
                    'id': t.id,
                    'title': t.title,
                    'filename': t.filename
                } for t in raw_tracks
            ],
            'association_table_data': [
                {
                    'playlist_id': row.playlist_id,
                    'track_id': row.track_id,
                    'position': row.position
                } for row in association_data
            ],
            'counts': {
                'get_tracks_count': len(tracks),
                'relationship_count': len(raw_tracks),
                'association_count': len(association_data)
            }
        }
        
        return jsonify({
            'success': True,
            'debug': debug_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@playlists_bp.route('/test-create', methods=['POST'])
def test_create_playlist():
    """Create a test playlist with sample tracks for debugging."""
    try:
        # Create a test playlist
        playlist = PlaylistService.create_playlist("Test Playlist")
        
        # Add some test tracks (using fake paths for testing)
        test_tracks = [
            "/fake/path/track1.mp3",
            "/fake/path/track2.mp3", 
            "/fake/path/track3.mp3"
        ]
        
        for track_path in test_tracks:
            # Create track manually for testing
            from app.utils.models import Track, db
            track = Track(
                title=f"Test Track - {track_path.split('/')[-1]}",
                filename=track_path,
                artist="Test Artist",
                album="Test Album",
                length="3:30"
            )
            db.session.add(track)
            db.session.flush()  # Get the ID
            
            # Add to playlist using the service
            PlaylistService.add_track_to_playlist(playlist.id, track_path)
        
        return jsonify({
            'success': True,
            'playlist': playlist.to_dict(),
            'message': f'Created test playlist with {len(test_tracks)} tracks'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 