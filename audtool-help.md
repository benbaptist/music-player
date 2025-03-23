tech@ubuntu:~$ audtool --help
Usage: audtool [-#] COMMAND ...
       where # (1-9) selects the instance of Audacious to control

Current song information:
   current-song                       - print formatted song title
   current-song-filename              - print song file name
   current-song-length                - print song length
   current-song-length-seconds        - print song length in seconds
   current-song-length-frames         - print song length in milliseconds
   current-song-output-length         - print playback time
   current-song-output-length-seconds - print playback time in seconds
   current-song-output-length-frames  - print playback time in milliseconds
   current-song-bitrate               - print bitrate in bits per second
   current-song-bitrate-kbps          - print bitrate in kilobits per second
   current-song-frequency             - print sampling rate in hertz
   current-song-frequency-khz         - print sampling rate in kilohertz
   current-song-channels              - print number of channels
   current-song-tuple-data            - print value of named field
   current-song-info                  - print bitrate, sampling rate, and channels

Playback commands:
   playback-play                      - start/restart/unpause playback
   playback-pause                     - pause/unpause playback
   playback-playpause                 - start/pause/unpause playback
   playback-stop                      - stop playback
   playback-playing                   - exit code = 0 if playing
   playback-paused                    - exit code = 0 if paused
   playback-stopped                   - exit code = 0 if not playing
   playback-status                    - print status (playing/paused/stopped)
   playback-seek                      - seek to given time
   playback-seek-relative             - seek to relative time offset
   playback-record                    - toggle stream recording
   playback-recording                 - exit code = 0 if recording

Playlist commands:
   select-displayed                   - apply commands to displayed playlist
   select-playing                     - apply commands to playing playlist
   playlist-advance                   - skip to next song
   playlist-advance-album             - skip to next album
   playlist-reverse                   - skip to previous song
   playlist-reverse-album             - skip to beginning of the previous album
   playlist-addurl                    - add URI at end of playlist
   playlist-insurl                    - insert URI at given position
   playlist-addurl-to-new-playlist    - open URI in "Now Playing" playlist
   playlist-delete                    - remove song at given position
   playlist-length                    - print number of songs in playlist
   playlist-song                      - print formatted title of given song
   playlist-song-filename             - print file name of given song
   playlist-song-length               - print length of given song
   playlist-song-length-seconds       - print length of given song in seconds
   playlist-song-length-frames        - print length of given song in milliseconds
   playlist-tuple-data                - print value of named field for given song
   playlist-display                   - print all songs in playlist
   playlist-position                  - print position of current song
   playlist-jump                      - skip to given song
   playlist-clear                     - clear playlist
   playlist-auto-advance-status       - query playlist auto-advance
   playlist-auto-advance-toggle       - toggle playlist auto-advance
   playlist-repeat-status             - query playlist repeat
   playlist-repeat-toggle             - toggle playlist repeat
   playlist-shuffle-status            - query playlist shuffle
   playlist-shuffle-toggle            - toggle playlist shuffle
   playlist-stop-after-status         - query if stopping after current song
   playlist-stop-after-toggle         - toggle if stopping after current song

More playlist commands:
   number-of-playlists                - print number of playlists
   current-playlist                   - print number of current playlist
   play-current-playlist              - play/resume current playlist
   set-current-playlist               - make given playlist current
   current-playlist-name              - print current playlist title
   set-current-playlist-name          - set current playlist title
   new-playlist                       - insert new playlist
   delete-current-playlist            - remove current playlist

Playlist queue commands:
   playqueue-add                      - add given song to queue
   playqueue-remove                   - remove given song from queue
   playqueue-is-queued                - exit code = 0 if given song is queued
   playqueue-get-queue-position       - print queue position of given song
   playqueue-get-list-position        - print n-th queued song
   playqueue-length                   - print number of songs in queue
   playqueue-display                  - print all songs in queue
   playqueue-clear                    - clear queue

Volume control and equalizer:
   get-volume                         - print current volume level in percent
   set-volume                         - set current volume level in percent
   equalizer-activate                 - activate/deactivate equalizer
   equalizer-get                      - print equalizer settings
   equalizer-set                      - set equalizer settings
   equalizer-get-preamp               - print equalizer pre-amplification
   equalizer-set-preamp               - set equalizer pre-amplification
   equalizer-get-band                 - print gain of given equalizer band
   equalizer-set-band                 - set gain of given equalizer band

Miscellaneous:
   mainwin-show                       - show/hide Audacious
   filebrowser-show                   - show/hide Add Files window
   jumptofile-show                    - show/hide Jump to Song window
   preferences-show                   - show/hide Settings window
   about-show                         - show/hide About window
   version                            - print Audacious version
   plugin-is-enabled                  - exit code = 0 if plugin is enabled
   plugin-enable                      - enable/disable plugin
   config-get                         - DO NOT USE
   config-set                         - DO NOT USE
   shutdown                           - shut down Audacious
   help                               - print this help

Commands may be prefixed with '--' (GNU-style long options) or not, your choice.
Show/hide and enable/disable commands take an optional 'on' or 'off' argument.
Report bugs to https://redmine.audacious-media-player.org/projects/audacious
