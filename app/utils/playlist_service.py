from app.utils.models import Playlist, Track, WatchPath
from app.utils.data_service import data_service
from app.utils import audtool
import os
from flask import current_app
import glob
from pathlib import Path
import subprocess
import json
from mutagen import File as MutagenFile
from datetime import timedelta

# Store the current playlist ID in memory
# This is a simple solution since we can't modify the database schema
_current_playlist_id = None

class PlaylistService:
    @staticmethod
    def get_all_playlists():
        """Get all playlists in the database."""
        playlists_db = data_service.get_playlists_db()
        playlists = []
        for playlist_id, playlist_data in playlists_db.data.items():
            if isinstance(playlist_data, Playlist):
                playlists.append(playlist_data)
        return playlists
    
    @staticmethod
    def get_playlist(playlist_id):
        """Get a playlist by ID."""
        playlists_db = data_service.get_playlists_db()
        return playlists_db.data.get(playlist_id)
    
    @staticmethod
    def create_playlist(name):
        """Create a new playlist."""
        playlist = Playlist(name=name)
        playlists_db = data_service.get_playlists_db()
        playlists_db[playlist.id] = playlist
        return playlist
    
    @staticmethod
    def rename_playlist(playlist_id, name):
        """Rename a playlist."""
        playlists_db = data_service.get_playlists_db()
        playlist = playlists_db.data.get(playlist_id)
        if playlist:
            playlist.name = name
            playlist.update_timestamp()
            return playlist
        return None
    
    @staticmethod
    def delete_playlist(playlist_id):
        """Delete a playlist."""
        playlists_db = data_service.get_playlists_db()
        if playlist_id in playlists_db.data:
            # Also remove associated watch paths
            watch_paths_db = data_service.get_watch_paths_db()
            watch_paths_to_remove = []
            for wp_id, wp in watch_paths_db.data.items():
                if isinstance(wp, WatchPath) and wp.playlist_id == playlist_id:
                    watch_paths_to_remove.append(wp_id)
            
            for wp_id in watch_paths_to_remove:
                del watch_paths_db[wp_id]
            
            del playlists_db[playlist_id]
            return True
        return False
    
    @staticmethod
    def get_playlist_tracks(playlist_id):
        """Get all tracks in a playlist."""
        playlist = PlaylistService.get_playlist(playlist_id)
        if not playlist:
            return []
        
        tracks_db = data_service.get_tracks_db()
        tracks = []
        for track_id in playlist.track_ids:
            track = tracks_db.data.get(track_id)
            if track and isinstance(track, Track):
                tracks.append(track)
        return tracks
    
    @staticmethod
    def get_current_playlist():
        """Get the current active playlist."""
        global _current_playlist_id
        if not _current_playlist_id:
            # Try to find the first playlist if none is set
            playlists = PlaylistService.get_all_playlists()
            if playlists:
                _current_playlist_id = playlists[0].id
            else:
                return None
        
        return PlaylistService.get_playlist(_current_playlist_id)
    
    @staticmethod
    def set_current_playlist(playlist_id):
        """Set a playlist as the current active playlist."""
        global _current_playlist_id
        
        playlist = PlaylistService.get_playlist(playlist_id)
        if playlist:
            _current_playlist_id = playlist.id
            return playlist
        return None
    
    @staticmethod
    def add_track_to_playlist(playlist_id, track_path):
        """Add a track to a playlist."""
        playlist = PlaylistService.get_playlist(playlist_id)
        if not playlist:
            return None
        
        tracks_db = data_service.get_tracks_db()
        
        # Check if track already exists in the database
        track = None
        for existing_track in tracks_db.data.values():
            if isinstance(existing_track, Track) and existing_track.filename == track_path:
                track = existing_track
                break
        
        if not track:
            # Get track metadata using mutagen
            try:
                # Default values
                title = os.path.basename(track_path)
                artist = None
                album = None
                length = "0:00"
                length_seconds = 0
                
                # Extract metadata using mutagen
                audio = MutagenFile(track_path)
                if audio:
                    # Try to get title - different files have different tag formats
                    if hasattr(audio, 'tags') and audio.tags:
                        if 'title' in audio:
                            title = audio['title'][0]
                        elif 'TIT2' in audio:
                            title = audio['TIT2'].text[0]
                        
                        # Try to get artist
                        if 'artist' in audio:
                            artist = audio['artist'][0]
                        elif 'TPE1' in audio:
                            artist = audio['TPE1'].text[0]
                        
                        # Try to get album
                        if 'album' in audio:
                            album = audio['album'][0]
                        elif 'TALB' in audio:
                            album = audio['TALB'].text[0]
                    
                    # Get length
                    if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                        length_seconds = int(audio.info.length)
                        minutes, seconds = divmod(length_seconds, 60)
                        length = f"{int(minutes)}:{int(seconds):02d}"
                
                # Create the track in our database
                track = Track(
                    title=title,
                    artist=artist,
                    album=album,
                    length=length,
                    length_seconds=length_seconds,
                    filename=track_path
                )
                tracks_db[track.id] = track
                
            except Exception as e:
                current_app.logger.error(f"Error getting metadata for {track_path}: {e}")
                # Create track with minimal info if metadata extraction fails
                filename = os.path.basename(track_path)
                track = Track(
                    title=filename,
                    filename=track_path
                )
                tracks_db[track.id] = track
        
        # Check if track is already in the playlist
        if track.id in playlist.track_ids:
            return track

        # Add track to playlist
        playlist.track_ids.append(track.id)
        playlist.update_timestamp()
        
        return track
    
    @staticmethod
    def remove_track_from_playlist(playlist_id, track_id):
        """Remove a track from a playlist."""
        playlist = PlaylistService.get_playlist(playlist_id)
        if playlist and track_id in playlist.track_ids:
            playlist.track_ids.remove(track_id)
            playlist.update_timestamp()
            return True
        return False
    
    @staticmethod
    def reorder_track(playlist_id, track_id, new_position):
        """Reorder a track within a playlist."""
        playlist = PlaylistService.get_playlist(playlist_id)
        if not playlist or track_id not in playlist.track_ids:
            return False
        
        # Remove track from current position
        current_position = playlist.track_ids.index(track_id)
        playlist.track_ids.pop(current_position)
        
        # Insert at new position
        playlist.track_ids.insert(new_position, track_id)
        playlist.update_timestamp()
        
        return True
    
    @staticmethod
    def update_playlist_settings(playlist_id, settings):
        """Update playlist settings."""
        playlist = PlaylistService.get_playlist(playlist_id)
        if playlist:
            if 'shuffle' in settings:
                playlist.shuffle = settings['shuffle']
            if 'repeat' in settings:
                playlist.repeat = settings['repeat']
            if 'stop_after_current' in settings:
                playlist.stop_after_current = settings['stop_after_current']
            if 'auto_advance' in settings:
                playlist.auto_advance = settings['auto_advance']
            
            playlist.update_timestamp()
            return playlist
        return None
    
    @staticmethod
    def add_watch_path(playlist_id, path, recursive=True, auto_add=True):
        """Add a path to watch for new audio files."""
        playlist = PlaylistService.get_playlist(playlist_id)
        if not playlist:
            return None
        
        path = os.path.abspath(os.path.expanduser(path))
        
        watch_paths_db = data_service.get_watch_paths_db()
        
        # Check if path already exists for the playlist
        existing = None
        for wp in watch_paths_db.data.values():
            if isinstance(wp, WatchPath) and wp.playlist_id == playlist_id and wp.path == path:
                existing = wp
                break
        
        if existing:
            existing.recursive = recursive
            existing.auto_add = auto_add
            return existing
        
        # Create new watch path
        watch_path = WatchPath(
            path=path,
            recursive=recursive,
            auto_add=auto_add,
            playlist_id=playlist_id
        )
        watch_paths_db[watch_path.id] = watch_path
        
        # If auto_add is True, scan the directory and add files
        if auto_add:
            PlaylistService.scan_watch_path(watch_path.id)
        
        return watch_path
    
    @staticmethod
    def remove_watch_path(watch_path_id):
        """Remove a watch path."""
        watch_paths_db = data_service.get_watch_paths_db()
        if watch_path_id in watch_paths_db.data:
            del watch_paths_db[watch_path_id]
            return True
        return False
    
    @staticmethod
    def scan_watch_path(watch_path_id):
        """Scan a watch path and add files to the playlist."""
        watch_paths_db = data_service.get_watch_paths_db()
        watch_path = watch_paths_db.data.get(watch_path_id)
        if not watch_path or not isinstance(watch_path, WatchPath):
            return False
        
        # Get all audio files in the path
        audio_files = []
        
        # Get allowed extensions from config
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', [])
        
        # Build the pattern for glob
        if watch_path.recursive:
            pattern = f"{watch_path.path}/**/*"
        else:
            pattern = f"{watch_path.path}/*"
        
        # Find all files matching the pattern
        for file_path in glob.glob(pattern, recursive=watch_path.recursive):
            if os.path.isfile(file_path):
                extension = os.path.splitext(file_path)[1][1:].lower()
                if extension in allowed_extensions:
                    audio_files.append(file_path)
        
        # Add files to playlist
        for file_path in audio_files:
            PlaylistService.add_track_to_playlist(watch_path.playlist_id, file_path)
        
        return True
    
    @staticmethod
    def get_watch_paths_for_playlist(playlist_id):
        """Get all watch paths for a playlist."""
        watch_paths_db = data_service.get_watch_paths_db()
        watch_paths = []
        for wp in watch_paths_db.data.values():
            if isinstance(wp, WatchPath) and wp.playlist_id == playlist_id:
                watch_paths.append(wp)
        return watch_paths
    
    @staticmethod
    def load_playlist_to_audacious(playlist_id):
        """Load a playlist to Audacious."""
        playlist = PlaylistService.get_playlist(playlist_id)
        if not playlist:
            return False
        
        # Set as current playlist in our application
        PlaylistService.set_current_playlist(playlist_id)
        
        # Always clear current Audacious playlist to ensure complete reset
        audtool.clear_playlist()
        
        # Apply playlist settings
        if playlist.shuffle:
            if audtool.get_shuffle_status() != "on":
                audtool.toggle_shuffle()
        else:
            if audtool.get_shuffle_status() != "off":
                audtool.toggle_shuffle()
                
        if playlist.repeat:
            if audtool.get_repeat_status() != "on":
                audtool.toggle_repeat()
        else:
            if audtool.get_repeat_status() != "off":
                audtool.toggle_repeat()
                
        if playlist.stop_after_current:
            if audtool.get_stop_after_status() != "on":
                audtool.toggle_stop_after()
        else:
            if audtool.get_stop_after_status() != "off":
                audtool.toggle_stop_after()
        
        if playlist.auto_advance:
            if audtool.get_auto_advance_status() != "on":
                audtool.toggle_auto_advance()
        else:
            if audtool.get_auto_advance_status() != "off":
                audtool.toggle_auto_advance()
        
        # Add each track to Audacious
        tracks = PlaylistService.get_playlist_tracks(playlist_id)
        current_app.logger.info(f"Loading {len(tracks)} tracks to Audacious for playlist {playlist_id}")
        
        for i, track in enumerate(tracks):
            current_app.logger.info(f"Adding track {i+1}: {track.filename}")
            audtool.add_song(track.filename)
        
        return True
    
    @staticmethod
    def migrate_audacious_playlists():
        """Import playlists from Audacious to the new system."""
        num_playlists = audtool.get_number_of_playlists()
        if not num_playlists:
            return []
        
        imported_playlists = []
        
        for i in range(int(num_playlists)):
            # Save current playlist
            current = audtool.get_current_playlist()
            
            # Switch to playlist to import
            audtool.set_current_playlist(i)
            playlist_name = audtool.get_current_playlist_name() or f"Playlist {i+1}"
            
            # Create new playlist in our system
            playlist = PlaylistService.create_playlist(playlist_name)
            
            # Get settings
            playlist.shuffle = audtool.get_shuffle_status() == "on"
            playlist.repeat = audtool.get_repeat_status() == "on"
            playlist.stop_after_current = audtool.get_stop_after_status() == "on"
            playlist.auto_advance = audtool.get_auto_advance_status() == "on"
            
            # Get all songs
            songs = audtool.get_all_songs()
            
            # Add songs to playlist
            for song in songs:
                # Add track to playlist (this will create the track if it doesn't exist)
                PlaylistService.add_track_to_playlist(playlist.id, song['filename'])
            
            imported_playlists.append(playlist)
            
            # Restore current playlist
            audtool.set_current_playlist(current)
        
        return imported_playlists
        
