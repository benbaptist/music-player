# Audacious Web Player

A modern, responsive web UI for controlling Audacious music player remotely. This application allows you to control Audacious from any device with a web browser on your network.

## Features

- Modern, clean, and responsive UI (mobile-friendly)
- Playback controls (play, pause, previous, next, seek)
- Volume control
- Access to all playlists
- File browser to play files from the server's filesystem
- Control settings like repeat, shuffle, stop after current song, etc.

## Requirements

- Python 3.6+
- Flask
- Audacious music player
- `audtool` command-line utility (comes with Audacious)
- `storify` package for simple database

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/audacious-web-player.git
   cd audacious-web-player
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python run.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Configuration

You can configure the application by setting environment variables or by modifying the `config.py` file:

- `SECRET_KEY`: Flask secret key for session security
- `DEBUG`: Enable/disable debug mode (`True` or `False`)
- `AUDACIOUS_DEFAULT_DIR`: Default music directory
- `AUDTOOL_COMMAND`: Path to the audtool command if not in PATH
- `FILE_BROWSER_ROOT`: Root directory for the file browser

## Usage

1. Make sure Audacious is running before starting the web server
2. Use the web interface to control playback, manage playlists, and browse files
3. For mobile access, ensure your device is on the same network and access the server's IP address

## License

MIT License

## Acknowledgments

- Audacious Music Player - https://audacious-media-player.org/
- Flask - https://flask.palletsprojects.com/
- Tailwind CSS - https://tailwindcss.com/
- Material Icons - https://fonts.google.com/icons 