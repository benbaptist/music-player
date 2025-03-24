import subprocess
import shlex
from flask import current_app
import os

def run_audtool(command, *args):
    """Run an audtool command and return its output."""
    cmd = [current_app.config['AUDTOOL_COMMAND'], command]
    cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Don't log errors for status checking commands that use exit codes as return values
        status_commands = ['playback-playing', 'playback-paused', 'playback-stopped', 'playback-recording']
        if command not in status_commands:
            current_app.logger.error(f"Error running audtool command {cmd}: {e}")
            current_app.logger.error(f"stderr: {e.stderr}")
        return None

# Player control functions
def get_current_song():
    return run_audtool('current-song')

def get_current_song_info():
    """Get detailed information about the current song."""
    # First check if there's a song playing or if the playlist is empty
    status = get_playback_status()
    length = get_playlist_length()
    
    if not length or int(length or 0) == 0:
        return {
            'title': None,
            'artist': None,
            'album': None,
            'length': None,
            'length_seconds': 0,
            'position': None,
            'position_seconds': 0,
            'bitrate': None,
            'filename': None
        }
    
    # Try to get current song info
    try:
        info = {
            'title': run_audtool('current-song'),
            'artist': run_audtool('current-song-tuple-data', 'artist'),
            'album': run_audtool('current-song-tuple-data', 'album'),
            'length': run_audtool('current-song-length'),
            'length_seconds': run_audtool('current-song-length-seconds') or 0,
            'position': run_audtool('current-song-output-length'),
            'position_seconds': run_audtool('current-song-output-length-seconds') or 0,
            'bitrate': run_audtool('current-song-bitrate-kbps'),
            'filename': run_audtool('current-song-filename')
        }
        
        # If title is None but we have a filename, use the filename as the title
        if info['title'] is None and info['filename']:
            info['title'] = os.path.basename(info['filename'])
            
        return info
    except Exception as e:
        current_app.logger.error(f"Error getting current song info: {e}")
        return {
            'title': None,
            'artist': None,
            'album': None,
            'length': None,
            'length_seconds': 0,
            'position': None,
            'position_seconds': 0,
            'bitrate': None,
            'filename': None
        }

def get_playback_status():
    if run_audtool('playback-playing') is not None:
        return 'playing'
    elif run_audtool('playback-paused') is not None:
        return 'paused'
    else:
        return 'stopped'

def play():
    return run_audtool('playback-play')

def pause():
    return run_audtool('playback-pause')

def playpause():
    return run_audtool('playback-playpause')

def stop():
    return run_audtool('playback-stop')

def seek(position):
    return run_audtool('playback-seek', str(position))

def seek_relative(offset):
    return run_audtool('playback-seek-relative', str(offset))

def next_song():
    return run_audtool('playlist-advance')

def previous_song():
    return run_audtool('playlist-reverse')

def get_volume():
    return run_audtool('get-volume')

def set_volume(volume):
    return run_audtool('set-volume', str(volume))

# Playlist functions
def get_playlist_length():
    return run_audtool('playlist-length')

def get_playlist_position():
    return run_audtool('playlist-position')

def jump_to_song(position):
    return run_audtool('playlist-jump', str(position))

def get_playlist_song(position):
    try:
        length = get_playlist_length()
        if not length or int(length) == 0:
            return None
            
        # Make sure position is within valid range
        position = int(position)
        if position < 0 or position >= int(length):
            return None
            
        return run_audtool('playlist-song', str(position + 1))  # Audacious uses 1-based indexing
    except (ValueError, TypeError):
        return None

def get_all_songs():
    """Get all songs in the current playlist."""
    length = get_playlist_length()
    if not length:
        return []
    
    try:
        length = int(length)
    except (ValueError, TypeError):
        return []
    
    songs = []
    for i in range(length):
        # Try to get song information, handling possible errors
        try:
            title = run_audtool('playlist-song', str(i + 1))  # Audacious uses 1-based indexing
            filename = run_audtool('playlist-song-filename', str(i + 1))
            song_length = run_audtool('playlist-song-length', str(i + 1))
            
            # Skip if we couldn't get the required information
            if filename is None:
                continue
                
            song = {
                'position': i,
                'title': title or os.path.basename(filename or ''),
                'filename': filename or '',
                'length': song_length or '0:00'
            }
            songs.append(song)
        except Exception as e:
            current_app.logger.error(f"Error getting song at position {i}: {e}")
            continue
    
    return songs

def clear_playlist():
    return run_audtool('playlist-clear')

def add_song(url):
    return run_audtool('playlist-addurl', url)

def delete_song(position):
    return run_audtool('playlist-delete', str(position))

# Playlist management
def get_number_of_playlists():
    return run_audtool('number-of-playlists')

def get_current_playlist():
    return run_audtool('current-playlist')

def set_current_playlist(playlist):
    return run_audtool('set-current-playlist', str(playlist))

def get_current_playlist_name():
    return run_audtool('current-playlist-name')

def set_current_playlist_name(name):
    return run_audtool('set-current-playlist-name', shlex.quote(name))

def new_playlist():
    return run_audtool('new-playlist')

def delete_current_playlist():
    return run_audtool('delete-current-playlist')

# Settings
def get_repeat_status():
    return run_audtool('playlist-repeat-status')

def toggle_repeat():
    return run_audtool('playlist-repeat-toggle')

def get_shuffle_status():
    return run_audtool('playlist-shuffle-status')

def toggle_shuffle():
    return run_audtool('playlist-shuffle-toggle')

def get_stop_after_status():
    return run_audtool('playlist-stop-after-status')

def toggle_stop_after():
    return run_audtool('playlist-stop-after-toggle')

def get_auto_advance_status():
    return run_audtool('playlist-auto-advance-status')

def toggle_auto_advance():
    return run_audtool('playlist-auto-advance-toggle') 