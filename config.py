import os

# Flask settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Audacious settings
AUDACIOUS_DEFAULT_DIR = os.getenv('AUDACIOUS_DEFAULT_DIR', os.path.expanduser('~/Music'))
AUDTOOL_COMMAND = os.getenv('AUDTOOL_COMMAND', 'audtool')

# File browser settings
FILE_BROWSER_ROOT = os.getenv('FILE_BROWSER_ROOT', AUDACIOUS_DEFAULT_DIR)
ALLOWED_EXTENSIONS = {
    'mp3', 'flac', 'ogg', 'wav', 'm4a', 'aac', 'wma', 
    'opus', 'aiff', 'ape', 'mpc', 'wv', 'tta'
} 