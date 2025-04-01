/**
 * Debug UI for Music Player Application
 * 
 * This is a simplified client for testing backend functionality.
 * It focuses on functionality rather than aesthetics.
 */

// Debug logging helper
function logDebug(message, data = null) {
    const output = document.getElementById('debug-output');
    const timestamp = new Date().toLocaleTimeString();
    let logMessage = `[${timestamp}] ${message}`;
    
    if (data) {
        if (typeof data === 'object') {
            logMessage += '\n' + JSON.stringify(data, null, 2);
        } else {
            logMessage += '\n' + data;
        }
    }
    
    output.textContent = logMessage + '\n\n' + output.textContent;
}

// API Helper Functions
async function fetchAPI(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        logDebug(`API ${method} ${endpoint}`, result);
        return result;
    } catch (error) {
        logDebug(`Error in API ${method} ${endpoint}`, error.message);
        return { success: false, error: error.message };
    }
}

// Global state
let currentPlaylist = null;
let updateInterval = null;

// Initialize the application
async function init() {
    // Load playlists
    await loadPlaylists();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Start status update interval
    startStatusUpdates();
    
    logDebug('Application initialized');
}

// Load all playlists
async function loadPlaylists() {
    const response = await fetchAPI('/playlists/');
    
    if (response.success) {
        const select = document.getElementById('playlist-select');
        select.innerHTML = '';
        
        response.playlists.forEach(playlist => {
            const option = document.createElement('option');
            option.value = playlist.id;
            option.textContent = `${playlist.name} (${playlist.tracks_count} tracks)`;
            option.dataset.playlist = JSON.stringify(playlist);
            if (playlist.is_current) {
                option.selected = true;
                currentPlaylist = playlist;
                updateCurrentPlaylistUI();
                loadPlaylistTracks(playlist.id);
            }
            select.appendChild(option);
        });
    }
}

// Load tracks for a specific playlist
async function loadPlaylistTracks(playlistId) {
    const response = await fetchAPI(`/playlists/${playlistId}`);
    
    if (response.success) {
        const tbody = document.querySelector('#tracks-table tbody');
        tbody.innerHTML = '';
        
        response.playlist.tracks.forEach((track, index) => {
            const tr = document.createElement('tr');
            
            tr.innerHTML = `
                <td>${track.id}</td>
                <td>${track.title || 'Unknown'}</td>
                <td>${track.artist || 'Unknown'}</td>
                <td>${track.album || 'Unknown'}</td>
                <td>${track.length || '0:00'}</td>
                <td>
                    <button class="play-track-btn" data-id="${track.id}" data-index="${index}">Play</button>
                    <button class="remove-track-btn" data-id="${track.id}">Remove</button>
                    <button class="move-up-btn" data-id="${track.id}" data-index="${index}" ${index === 0 ? 'disabled' : ''}>▲</button>
                    <button class="move-down-btn" data-id="${track.id}" data-index="${index}" ${index === response.playlist.tracks.length - 1 ? 'disabled' : ''}>▼</button>
                </td>
            `;
            
            tbody.appendChild(tr);
        });
        
        // Add event listeners to buttons
        document.querySelectorAll('.play-track-btn').forEach(btn => {
            btn.addEventListener('click', () => playTrack(playlistId, parseInt(btn.dataset.index)));
        });
        
        document.querySelectorAll('.remove-track-btn').forEach(btn => {
            btn.addEventListener('click', () => removeTrack(playlistId, parseInt(btn.dataset.id)));
        });
        
        document.querySelectorAll('.move-up-btn').forEach(btn => {
            btn.addEventListener('click', () => reorderTrack(playlistId, parseInt(btn.dataset.id), parseInt(btn.dataset.index) - 1));
        });
        
        document.querySelectorAll('.move-down-btn').forEach(btn => {
            btn.addEventListener('click', () => reorderTrack(playlistId, parseInt(btn.dataset.id), parseInt(btn.dataset.index) + 1));
        });
        
        // Also load playlist settings
        loadPlaylistSettings(playlistId);
    }
}

// Load settings for a playlist
async function loadPlaylistSettings(playlistId) {
    const response = await fetchAPI(`/playlists/${playlistId}`);
    
    if (response.success && response.playlist && response.playlist.settings) {
        const settings = response.playlist.settings;
        
        // Update checkboxes
        document.getElementById('setting-repeat').checked = settings.repeat;
        document.getElementById('setting-shuffle').checked = settings.shuffle;
        document.getElementById('setting-stop-after').checked = settings.stop_after_current;
        document.getElementById('setting-auto-advance').checked = settings.auto_advance;
    }
}

// Save playlist settings
async function savePlaylistSettings(playlistId) {
    const settings = {
        repeat: document.getElementById('setting-repeat').checked,
        shuffle: document.getElementById('setting-shuffle').checked,
        stop_after_current: document.getElementById('setting-stop-after').checked,
        auto_advance: document.getElementById('setting-auto-advance').checked
    };
    
    const response = await fetchAPI(`/playlists/${playlistId}/settings`, 'POST', { settings });
    
    if (response.success) {
        logDebug(`Saved settings for playlist ${playlistId}`, settings);
    }
}

// Create a new playlist
async function createPlaylist(name) {
    const response = await fetchAPI('/playlists/new', 'POST', { name });
    
    if (response.success) {
        logDebug(`Created new playlist: ${name}`);
        await loadPlaylists();
    }
}

// Rename a playlist
async function renamePlaylist(playlistId, newName) {
    const response = await fetchAPI(`/playlists/${playlistId}/rename`, 'POST', { name: newName });
    
    if (response.success) {
        logDebug(`Renamed playlist ${playlistId} to: ${newName}`);
        await loadPlaylists();
    }
}

// Delete a playlist
async function deletePlaylist(playlistId) {
    const response = await fetchAPI(`/playlists/${playlistId}/delete`, 'POST');
    
    if (response.success) {
        logDebug(`Deleted playlist ${playlistId}`);
        await loadPlaylists();
    }
}

// Set current playlist
async function setCurrentPlaylist(playlistId) {
    const response = await fetchAPI(`/playlists/set-current/${playlistId}`, 'POST');
    
    if (response.success) {
        logDebug(`Set current playlist to ${playlistId}`);
        await loadPlaylists();
        
        // Also load the tracks for this playlist
        loadPlaylistTracks(playlistId);
    }
}

// Add a track to a playlist
async function addTrack(playlistId, trackPath) {
    const response = await fetchAPI(`/playlists/${playlistId}/add`, 'POST', { path: trackPath });
    
    if (response.success) {
        logDebug(`Added track to playlist ${playlistId}`, response.track);
        await loadPlaylistTracks(playlistId);
    }
}

// Remove a track from a playlist
async function removeTrack(playlistId, trackId) {
    const response = await fetchAPI(`/playlists/${playlistId}/remove/${trackId}`, 'POST');
    
    if (response.success) {
        logDebug(`Removed track ${trackId} from playlist ${playlistId}`);
        await loadPlaylistTracks(playlistId);
    }
}

// Reorder a track within a playlist
async function reorderTrack(playlistId, trackId, newPosition) {
    const response = await fetchAPI(`/playlists/${playlistId}/reorder`, 'POST', { 
        track_id: trackId,
        position: newPosition 
    });
    
    if (response.success) {
        logDebug(`Reordered track ${trackId} to position ${newPosition}`);
        await loadPlaylistTracks(playlistId);
    }
}

// Play a specific track
async function playTrack(playlistId, index) {
    // First ensure this playlist is the current one
    await setCurrentPlaylist(playlistId);
    
    // Then load the playlist into the player
    const loadResponse = await fetchAPI(`/playlists/${playlistId}/play`, 'POST');
    
    if (loadResponse.success) {
        logDebug(`Loaded playlist ${playlistId} for playback`);
        
        // Jump to the specific track if index is provided
        if (index !== undefined) {
            await fetchAPI(`/player/jump-to/${index}`, 'POST');
            
            // Then start playback
            await fetchAPI('/player/play', 'POST');
        }
    }
}

// Player control functions
async function playPlayer() {
    return fetchAPI('/player/play', 'POST');
}

async function pausePlayer() {
    return fetchAPI('/player/pause', 'POST');
}

async function stopPlayer() {
    return fetchAPI('/player/stop', 'POST');
}

async function prevTrack() {
    return fetchAPI('/player/previous', 'POST');
}

async function nextTrack() {
    return fetchAPI('/player/next', 'POST');
}

async function setVolume(value) {
    return fetchAPI('/player/volume', 'POST', { volume: value });
}

async function seekTo(position) {
    return fetchAPI('/player/seek', 'POST', { position });
}

// Update UI with current player status
async function updatePlayerStatus() {
    const response = await fetchAPI('/player/status');
    
    if (response.success) {
        const song = response.song;
        const status = response.status;
        
        // Update now playing info
        document.getElementById('current-title').textContent = song.title || '-';
        document.getElementById('current-artist').textContent = song.artist || '-';
        document.getElementById('current-album').textContent = song.album || '-';
        document.getElementById('current-filename').textContent = song.filename || '-';
        
        // Update time display
        const currentTime = document.getElementById('current-time');
        const totalTime = document.getElementById('total-time');
        currentTime.textContent = song.position || '0:00';
        totalTime.textContent = song.length || '0:00';
        
        // Update seek slider
        const seekSlider = document.getElementById('seek-slider');
        if (song.length_seconds && parseInt(song.length_seconds) > 0) {
            seekSlider.disabled = false;
            seekSlider.max = song.length_seconds;
            seekSlider.value = song.position_seconds || 0;
        } else {
            seekSlider.disabled = true;
            seekSlider.value = 0;
        }
    }
}

// Update UI with current playlist
function updateCurrentPlaylistUI() {
    if (currentPlaylist) {
        document.getElementById('current-playlist-name').textContent = currentPlaylist.name;
    } else {
        document.getElementById('current-playlist-name').textContent = 'None';
    }
}

// Set up all event handlers
function setupEventHandlers() {
    // Playlist management
    document.getElementById('create-playlist-btn').addEventListener('click', () => {
        const name = document.getElementById('new-playlist-name').value.trim();
        if (name) {
            createPlaylist(name);
            document.getElementById('new-playlist-name').value = '';
        }
    });
    
    document.getElementById('delete-playlist-btn').addEventListener('click', () => {
        const select = document.getElementById('playlist-select');
        if (select.value) {
            if (confirm(`Are you sure you want to delete this playlist?`)) {
                deletePlaylist(select.value);
            }
        }
    });
    
    document.getElementById('rename-playlist-btn').addEventListener('click', () => {
        const select = document.getElementById('playlist-select');
        const newName = document.getElementById('rename-playlist-input').value.trim();
        if (select.value && newName) {
            renamePlaylist(select.value, newName);
            document.getElementById('rename-playlist-input').value = '';
        }
    });
    
    document.getElementById('set-current-playlist-btn').addEventListener('click', () => {
        const select = document.getElementById('playlist-select');
        if (select.value) {
            setCurrentPlaylist(select.value);
        }
    });
    
    // When a playlist is selected, load its tracks
    document.getElementById('playlist-select').addEventListener('change', (e) => {
        if (e.target.value) {
            const playlistData = JSON.parse(e.target.selectedOptions[0].dataset.playlist);
            loadPlaylistTracks(e.target.value);
        }
    });
    
    // Save playlist settings
    document.getElementById('save-settings-btn').addEventListener('click', () => {
        const select = document.getElementById('playlist-select');
        if (select.value) {
            savePlaylistSettings(select.value);
        }
    });
    
    // Add track to playlist
    document.getElementById('add-track-btn').addEventListener('click', () => {
        const select = document.getElementById('playlist-select');
        const trackPath = document.getElementById('add-track-path').value.trim();
        if (select.value && trackPath) {
            addTrack(select.value, trackPath);
            document.getElementById('add-track-path').value = '';
        }
    });
    
    // Player controls
    document.getElementById('play-btn').addEventListener('click', playPlayer);
    document.getElementById('pause-btn').addEventListener('click', pausePlayer);
    document.getElementById('stop-btn').addEventListener('click', stopPlayer);
    document.getElementById('previous-btn').addEventListener('click', prevTrack);
    document.getElementById('next-btn').addEventListener('click', nextTrack);
    
    // Volume control
    const volumeSlider = document.getElementById('volume-slider');
    const volumeValue = document.getElementById('volume-value');
    
    volumeSlider.addEventListener('input', () => {
        volumeValue.textContent = volumeSlider.value;
    });
    
    volumeSlider.addEventListener('change', () => {
        setVolume(volumeSlider.value);
    });
    
    // Seek control
    const seekSlider = document.getElementById('seek-slider');
    seekSlider.addEventListener('change', () => {
        seekTo(seekSlider.value);
    });
}

// Start interval to update status
function startStatusUpdates() {
    // First update immediately
    updatePlayerStatus();
    
    // Then set an interval to update every second
    updateInterval = setInterval(updatePlayerStatus, 1000);
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init); 