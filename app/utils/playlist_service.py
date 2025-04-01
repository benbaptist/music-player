from app.utils.models import db, Playlist, Track, WatchPath
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
        return Playlist.query.all()
    
    @staticmethod
    def get_playlist(playlist_id):
        """Get a playlist by ID."""
        return Playlist.query.get(playlist_id)
    
    @staticmethod
    def create_playlist(name):
        """Create a new playlist."""
        playlist = Playlist(name=name)
        db.session.add(playlist)
        db.session.commit()
        return playlist
    
    @staticmethod
    def rename_playlist(playlist_id, name):
        """Rename a playlist."""
        playlist = Playlist.query.get(playlist_id)
        if playlist:
            playlist.name = name
            db.session.commit()
            return playlist
        return None
    
    @staticmethod
    def delete_playlist(playlist_id):
        """Delete a playlist."""
        playlist = Playlist.query.get(playlist_id)
        if playlist:
            db.session.delete(playlist)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_playlist_tracks(playlist_id):
        """Get all tracks in a playlist."""
        playlist = Playlist.query.get(playlist_id)
        if playlist:
            return playlist.get_tracks()
        return []
    
    @staticmethod
    def get_current_playlist():
        """Get the current active playlist."""
        global _current_playlist_id
        if not _current_playlist_id:
            # Try to find the first playlist if none is set
            first_playlist = Playlist.query.first()
            if first_playlist:
                _current_playlist_id = first_playlist.id
            else:
                return None
        
        return Playlist.query.get(_current_playlist_id)
    
    @staticmethod
    def set_current_playlist(playlist_id):
        """Set a playlist as the current active playlist."""
        global _current_playlist_id
        
        # Set the new current playlist
        playlist = Playlist.query.get(playlist_id)
        if playlist:
            _current_playlist_id = playlist.id
            return playlist
        return None
    
    @staticmethod
    def add_track_to_playlist(playlist_id, track_path):
        """Add a track to a playlist."""
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return None
        
        # Check if track already exists in the database
        track = Track.query.filter_by(filename=track_path).first()
        
        if not track:
            # Get track metadata using mutagen instead of audacious
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
                db.session.add(track)
                
            except Exception as e:
                current_app.logger.error(f"Error getting metadata for {track_path}: {e}")
                # Create track with minimal info if metadata extraction fails
                filename = os.path.basename(track_path)
                track = Track(
                    title=filename,
                    filename=track_path
                )
                db.session.add(track)
        
        # Check if track is already in the playlist
        if track in playlist.tracks:
            return track
        
        # Get the next position in the playlist
        position = len(playlist.tracks)
        
        # Add track to playlist
        statement = playlist_tracks.insert().values(
            playlist_id=playlist.id,
            track_id=track.id,
            position=position
        )
        db.session.execute(statement)
        db.session.commit()
        
        return track
    
    @staticmethod
    def remove_track_from_playlist(playlist_id, track_id):
        """Remove a track from a playlist."""
        playlist = Playlist.query.get(playlist_id)
        track = Track.query.get(track_id)
        
        if playlist and track and track in playlist.tracks:
            # Get current position of track
            stmt = playlist_tracks.select().where(
                (playlist_tracks.c.playlist_id == playlist_id) & 
                (playlist_tracks.c.track_id == track_id)
            )
            result = db.session.execute(stmt).first()
            position = result.position if result else -1
            
            # Remove track from playlist
            playlist.tracks.remove(track)
            
            # Reorder positions of tracks after the removed one
            if position >= 0:
                stmt = playlist_tracks.update().where(
                    (playlist_tracks.c.playlist_id == playlist_id) & 
                    (playlist_tracks.c.position > position)
                ).values(
                    position=playlist_tracks.c.position - 1
                )
                db.session.execute(stmt)
            
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def reorder_track(playlist_id, track_id, new_position):
        """Reorder a track within a playlist."""
        playlist = Playlist.query.get(playlist_id)
        track = Track.query.get(track_id)
        
        if not playlist or not track or track not in playlist.tracks:
            return False
        
        # Get current position
        stmt = playlist_tracks.select().where(
            (playlist_tracks.c.playlist_id == playlist_id) & 
            (playlist_tracks.c.track_id == track_id)
        )
        result = db.session.execute(stmt).first()
        current_position = result.position if result else -1
        
        if current_position == -1:
            return False
        
        # Ensure new_position is within valid range
        track_count = len(playlist.tracks)
        if new_position < 0:
            new_position = 0
        elif new_position >= track_count:
            new_position = track_count - 1
        
        # No change needed if position is the same
        if current_position == new_position:
            return True
        
        # Update positions
        if current_position < new_position:
            # Moving down: decrement positions of tracks between current and new
            stmt = playlist_tracks.update().where(
                (playlist_tracks.c.playlist_id == playlist_id) & 
                (playlist_tracks.c.position > current_position) &
                (playlist_tracks.c.position <= new_position)
            ).values(
                position=playlist_tracks.c.position - 1
            )
            db.session.execute(stmt)
        else:
            # Moving up: increment positions of tracks between new and current
            stmt = playlist_tracks.update().where(
                (playlist_tracks.c.playlist_id == playlist_id) & 
                (playlist_tracks.c.position >= new_position) &
                (playlist_tracks.c.position < current_position)
            ).values(
                position=playlist_tracks.c.position + 1
            )
            db.session.execute(stmt)
        
        # Update position of the track itself
        stmt = playlist_tracks.update().where(
            (playlist_tracks.c.playlist_id == playlist_id) & 
            (playlist_tracks.c.track_id == track_id)
        ).values(
            position=new_position
        )
        db.session.execute(stmt)
        db.session.commit()
        
        return True
    
    @staticmethod
    def update_playlist_settings(playlist_id, settings):
        """Update playlist settings."""
        playlist = Playlist.query.get(playlist_id)
        if playlist:
            if 'shuffle' in settings:
                playlist.shuffle = settings['shuffle']
            if 'repeat' in settings:
                playlist.repeat = settings['repeat']
            if 'stop_after_current' in settings:
                playlist.stop_after_current = settings['stop_after_current']
            if 'auto_advance' in settings:
                playlist.auto_advance = settings['auto_advance']
            
            db.session.commit()
            return playlist
        return None
    
    @staticmethod
    def add_watch_path(playlist_id, path, recursive=True, auto_add=True):
        """Add a path to watch for new audio files."""
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return None
        
        path = os.path.abspath(os.path.expanduser(path))
        
        # Check if path already exists for the playlist
        existing = WatchPath.query.filter_by(playlist_id=playlist_id, path=path).first()
        if existing:
            existing.recursive = recursive
            existing.auto_add = auto_add
            db.session.commit()
            return existing
        
        # Create new watch path
        watch_path = WatchPath(
            path=path,
            recursive=recursive,
            auto_add=auto_add,
            playlist_id=playlist_id
        )
        db.session.add(watch_path)
        db.session.commit()
        
        # If auto_add is True, scan the directory and add files
        if auto_add:
            PlaylistService.scan_watch_path(watch_path.id)
        
        return watch_path
    
    @staticmethod
    def remove_watch_path(watch_path_id):
        """Remove a watch path."""
        watch_path = WatchPath.query.get(watch_path_id)
        if watch_path:
            db.session.delete(watch_path)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def scan_watch_path(watch_path_id):
        """Scan a watch path and add files to the playlist."""
        watch_path = WatchPath.query.get(watch_path_id)
        if not watch_path:
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
    def load_playlist_to_audacious(playlist_id):
        """Load a playlist to Audacious."""
        playlist = Playlist.query.get(playlist_id)
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
        for track in playlist.get_tracks():
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
                # Find or create track
                track = Track.query.filter_by(filename=song['filename']).first()
                if not track:
                    track = Track(
                        title=song['title'],
                        filename=song['filename'],
                        length=song['length']
                    )
                    db.session.add(track)
                
                # Add to playlist
                playlist.tracks.append(track)
            
            db.session.commit()
            imported_playlists.append(playlist)
            
            # Restore current playlist
            audtool.set_current_playlist(current)
        
        return imported_playlists
        
# Import from models to make the association table accessible
from app.utils.models import playlist_tracks 