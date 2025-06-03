import os
from dotenv import load_dotenv
import pathlib

# Load environment variables from .env file
load_dotenv()

# Convert comma-separated string to set
def str_to_set(value, default=None):
    if not value:
        return default
    return set(ext.strip() for ext in value.split(','))

# Helper function to expand user path
def expand_path(path):
    if path:
        return os.path.expanduser(path)
    return path

# Flask settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Data storage settings
DATA_DIR = expand_path(os.getenv('DATA_DIR', './data'))

# Audacious settings
AUDACIOUS_DEFAULT_DIR = expand_path(os.getenv('AUDACIOUS_DEFAULT_DIR', '~/Music'))
AUDTOOL_COMMAND = os.getenv('AUDTOOL_COMMAND', 'audtool')

# File browser settings
FILE_BROWSER_ROOT = expand_path(os.getenv('FILE_BROWSER_ROOT', AUDACIOUS_DEFAULT_DIR))
ALLOWED_EXTENSIONS = str_to_set(
    os.getenv('ALLOWED_EXTENSIONS'),
    {'mp3', 'flac', 'ogg', 'wav', 'm4a', 'aac', 'wma', 'opus', 'aiff', 'ape', 'mpc', 'wv', 'tta'}
) 