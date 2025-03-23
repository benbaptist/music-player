import subprocess
import shlex
from flask import current_app

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
    info = {
        'title': run_audtool('current-song'),
        'artist': run_audtool('current-song-tuple-data', 'artist'),
        'album': run_audtool('current-song-tuple-data', 'album'),
        'length': run_audtool('current-song-length'),
        'length_seconds': run_audtool('current-song-length-seconds'),
        'position': run_audtool('current-song-output-length'),
        'position_seconds': run_audtool('current-song-output-length-seconds'),
        'bitrate': run_audtool('current-song-bitrate-kbps'),
        'filename': run_audtool('current-song-filename')
    }
    return info

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
    return run_audtool('playlist-song', str(position))

def get_all_songs():
    """Get all songs in the current playlist."""
    length = get_playlist_length()
    if not length:
        return []
    
    songs = []
    for i in range(int(length)):
        song = {
            'position': i,
            'title': run_audtool('playlist-song', str(i)),
            'filename': run_audtool('playlist-song-filename', str(i)),
            'length': run_audtool('playlist-song-length', str(i))
        }
        songs.append(song)
    
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