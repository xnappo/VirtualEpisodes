# script.virtualepisodes
Set of utilities to provide dummy episodes for streaming provider content.

Problem:

Want to be able to track streaming provider TV episodes within Kodi, but just watch them in the native app rather than constantly chasing Kodi Netflix/Prime strm compatibility.

Solution:

- Python script autoVirtual monitors Sonarr calendar for new Netflix and Amazon episode availability and creates placeholder episode files
- Python script addVirtual uses Sonarr data to create Netflix and Amazon placeholder episode files on demand for already aired episodes
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
Kodi service to launch streaming app for virtual episodes

Web interface:
- Provides a simple UI to add show stubs and movie stubs without the CLI
- Runs [addVirtual.py](addVirtual.py) and [addMovieVirtual.py](addMovieVirtual.py) on demand and streams their output
- Lets you map unmapped networks into [config.yaml](config.yaml) and re-run immediately
- Shows recent Sonarr suggestions when a series name is not found

Run the web interface:
- Copy [config.yaml_EXAMPLE](config.yaml_EXAMPLE) to [config.yaml](config.yaml) and ensure the networks list is populated
- Install dependencies: Flask and PyYAML
- Start the server with python flask_app.py (or run [flask_app.py](flask_app.py) in your environment)
- Open http://localhost:8086 in a browser (or http://<host>:8086 if hosting on another machine)
