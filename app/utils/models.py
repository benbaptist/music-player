from storify.model import Model
from datetime import datetime
import uuid


class Playlist(Model):
    def __init__(self, playlist_id=None, name=None, created_at=None, updated_at=None,
                 shuffle=False, repeat=False, stop_after_current=False, auto_advance=True,
                 tracks=None, watch_paths=None):
        self.id = playlist_id or str(uuid.uuid4())
        self.name = name or "New Playlist"
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Playlist settings
        self.shuffle = shuffle
        self.repeat = repeat
        self.stop_after_current = stop_after_current
        self.auto_advance = auto_advance
        
        # Track IDs in order
        self.track_ids = tracks or []
        
        # Watch paths for this playlist
        self.watch_paths = watch_paths or []
    
    def _to_dict(self):
        """Convert to dictionary for Storify serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'shuffle': self.shuffle,
            'repeat': self.repeat,
            'stop_after_current': self.stop_after_current,
            'auto_advance': self.auto_advance,
            'track_ids': self.track_ids,
            'watch_paths': self.watch_paths
        }
    
    @classmethod
    def _from_dict(cls, data):
        """Create instance from dictionary for Storify deserialization."""
        return cls(
            playlist_id=data['id'],
            name=data['name'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            shuffle=data['shuffle'],
            repeat=data['repeat'],
            stop_after_current=data['stop_after_current'],
            auto_advance=data['auto_advance'],
            tracks=data['track_ids'],
            watch_paths=data['watch_paths']
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'settings': {
                'shuffle': self.shuffle,
                'repeat': self.repeat,
                'stop_after_current': self.stop_after_current,
                'auto_advance': self.auto_advance
            },
            'tracks_count': len(self.track_ids),
            'is_current': False  # This will be set dynamically by the service
        }
    
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()


class Track(Model):
    def __init__(self, track_id=None, title=None, artist=None, album=None, 
                 length=None, length_seconds=None, filename=None, created_at=None):
        self.id = track_id or str(uuid.uuid4())
        self.title = title
        self.artist = artist
        self.album = album
        self.length = length
        self.length_seconds = length_seconds
        self.filename = filename
        self.created_at = created_at or datetime.utcnow()
    
    def _to_dict(self):
        """Convert to dictionary for Storify serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'length': self.length,
            'length_seconds': self.length_seconds,
            'filename': self.filename,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def _from_dict(cls, data):
        """Create instance from dictionary for Storify deserialization."""
        return cls(
            track_id=data['id'],
            title=data['title'],
            artist=data['artist'],
            album=data['album'],
            length=data['length'],
            length_seconds=data['length_seconds'],
            filename=data['filename'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title or (self.filename.split('/')[-1] if self.filename else 'Unknown'),
            'artist': self.artist,
            'album': self.album,
            'length': self.length,
            'length_seconds': self.length_seconds,
            'filename': self.filename
        }


class WatchPath(Model):
    def __init__(self, watch_path_id=None, path=None, recursive=True, auto_add=True, 
                 playlist_id=None, created_at=None):
        self.id = watch_path_id or str(uuid.uuid4())
        self.path = path
        self.recursive = recursive
        self.auto_add = auto_add
        self.playlist_id = playlist_id
        self.created_at = created_at or datetime.utcnow()
    
    def _to_dict(self):
        """Convert to dictionary for Storify serialization."""
        return {
            'id': self.id,
            'path': self.path,
            'recursive': self.recursive,
            'auto_add': self.auto_add,
            'playlist_id': self.playlist_id,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def _from_dict(cls, data):
        """Create instance from dictionary for Storify deserialization."""
        return cls(
            watch_path_id=data['id'],
            path=data['path'],
            recursive=data['recursive'],
            auto_add=data['auto_add'],
            playlist_id=data['playlist_id'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'path': self.path,
            'recursive': self.recursive,
            'auto_add': self.auto_add,
            'playlist_id': self.playlist_id
        } 