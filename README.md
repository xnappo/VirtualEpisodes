# VirtualEpisodes
Set of utilities to provide dummy episodes for streaming provider content

Problem:

Want to be able to track streaming provider TV episodes within Kodi, but just watch them in the native app rather than constantly chasing Kodi Netflix/Prime strm compatibility.

Solution:

- Python script autoVirtual monitors Sonarr calendar for new Netflix and Amazon episode availability and creates placeholder episode files
- Python script addVirtual uses Sonarr data to creat Netflix and Amazon placeholder episode files
- Emby scrapes dummy files and adds to database as with any 'real' file
- Kodi service.py looks for playing file with 'Netflix' or 'Amazon' in the name and lauches native player

Limitations:

- Kodi service only set up to work with Android right now (and maybe only NVidia Shield)
- Does not launch episode directly, still have to navigate in native app again

Usage:
- Copy the config.yaml_EXAMPLE file to config.yaml edit as needed
- Add Netflix/Amazon shows to Sonarr as normal, but set to 'unmonitored'
- Create windows schedule or linux chron job to run autoVirtual.py once a day for upcoming shows/episodes
- Run addVirtual.py with substring of show to add as argument to add already aired episodes
- Set up service.py as Kodi addon - if people get interested in my hair-brained scheme I can host it on a repo

