from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# Association table for many-to-many relationship between playlists and tracks
playlist_tracks = db.Table('playlist_tracks',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlists.id'), primary_key=True),
    db.Column('track_id', db.Integer, db.ForeignKey('tracks.id'), primary_key=True),
    db.Column('position', db.Integer, nullable=False)
)

class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Playlist settings
    shuffle = db.Column(db.Boolean, default=False)
    repeat = db.Column(db.Boolean, default=False)
    stop_after_current = db.Column(db.Boolean, default=False)
    auto_advance = db.Column(db.Boolean, default=True)
    
    # Relationship to tracks through the association table
    tracks = db.relationship('Track', secondary=playlist_tracks, 
                            order_by=playlist_tracks.c.position,
                            backref=db.backref('playlists', lazy='dynamic'))
    
    # Relationship to watch paths
    watch_paths = db.relationship('WatchPath', backref='playlist', lazy=True, cascade="all, delete-orphan")
    
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
            'tracks_count': len(self.tracks),
            'is_current': False  # This will be set dynamically by the service
        }
    
    def get_tracks(self):
        # Get tracks in proper order
        return self.tracks

class Track(db.Model):
    __tablename__ = 'tracks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    artist = db.Column(db.String(255), nullable=True)
    album = db.Column(db.String(255), nullable=True)
    length = db.Column(db.String(20), nullable=True)  # Format: MM:SS
    length_seconds = db.Column(db.Integer, nullable=True)
    filename = db.Column(db.String(1024), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title or self.filename.split('/')[-1],
            'artist': self.artist,
            'album': self.album,
            'length': self.length,
            'length_seconds': self.length_seconds,
            'filename': self.filename
        }

class WatchPath(db.Model):
    __tablename__ = 'watch_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(1024), nullable=False)
    recursive = db.Column(db.Boolean, default=True)
    auto_add = db.Column(db.Boolean, default=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'path': self.path,
            'recursive': self.recursive,
            'auto_add': self.auto_add,
            'playlist_id': self.playlist_id
        } 