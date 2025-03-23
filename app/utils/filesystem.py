import os
from pathlib import Path
from flask import current_app

def get_directory_contents(directory=None):
    """Get contents of a directory, returning directories and audio files."""
    if directory is None:
        directory = current_app.config['FILE_BROWSER_ROOT']
    
    # Make sure we don't go outside the allowed root
    root_path = Path(current_app.config['FILE_BROWSER_ROOT']).resolve()
    target_path = Path(directory).resolve()
    
    if not str(target_path).startswith(str(root_path)):
        # Attempted directory traversal
        target_path = root_path
    
    # Get directory contents
    dirs = []
    files = []
    
    try:
        for item in sorted(os.listdir(target_path)):
            item_path = target_path / item
            
            if item.startswith('.'):
                continue  # Skip hidden files/directories
                
            if item_path.is_dir():
                dirs.append({
                    'name': item,
                    'path': str(item_path.relative_to(root_path)),
                    'type': 'directory'
                })
            elif item_path.is_file() and item_path.suffix.lower().lstrip('.') in current_app.config['ALLOWED_EXTENSIONS']:
                files.append({
                    'name': item,
                    'path': str(item_path),
                    'type': 'file',
                    'extension': item_path.suffix.lower().lstrip('.')
                })
    except (PermissionError, FileNotFoundError) as e:
        current_app.logger.error(f"Error accessing directory {target_path}: {e}")
        
    return {
        'current_directory': str(target_path),
        'parent_directory': str(target_path.parent) if str(target_path) != str(root_path) else None,
        'relative_path': str(target_path.relative_to(root_path)) if target_path != root_path else '',
        'dirs': dirs,
        'files': files
    } 