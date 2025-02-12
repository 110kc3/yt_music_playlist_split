# YouTube Playlist Splitter

A Python script that splits a **large YouTube Music (or YouTube) playlist** into two new playlists.  
It uses the [YouTube Data API v3](https://developers.google.com/youtube/v3) and handles adding items in **chunked batches** to avoid errors and rate limits.

The script is making a separate API call for every single video. Unfortunately, the YouTube Data API does not provide a “bulk insert” method for playlist items—each playlistItems.insert call can only add one item at a time, costing 50 quota units. Once you exceed 10,000 units in a day you’ll get quotaExceeded errors. Since each insert is 50 units, you can only add about 10,000 / 50 = 200 videos per day before hitting the limit.

Created in order to bypass a limit form another api like tunemymusic or soundiiz, in order to move playlists to Spotify.

---

## Features

- Fetches all videos from a **source playlist**.
- Splits them in **two halves** (first half, second half).
- Creates two new playlists (e.g., “My Playlist - Part 1” and “Part 2”).
- Adds videos in **chunks** (default 50) with short delays and retry logic.
- Helps avoid [quotaExceeded](https://developers.google.com/youtube/v3/getting-started#quota) and [serviceUnavailable](https://developers.google.com/youtube/v3/docs/errors) errors.

---

## Requirements

1. **Python 3.7+**  
2. [**Google API Python Client**](https://pypi.org/project/google-api-python-client/) and its dependencies. Install via:

pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
3. A Google Cloud project with YouTube Data API v3 enabled.
4. An OAuth 2.0 Client ID (Desktop App) JSON file, downloaded as client_secret.json. 
(on GCP Credentials → Create Credentials → OAuth client ID )

## Setup & Usage
1. Clone this repo 
2. Place your client_secret.json in the same folder.
3. In your terminal, install dependencies:

pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

4. Edit the script:
Set ORIGINAL_PLAYLIST_ID to the YouTube playlist ID you want to split. (does not need to be public)

Optionally tweak CHUNK_SIZE or DELAYS in the code if needed.

python split_youtube_playlist.py

A browser window will open for OAuth consent. Sign in with the account that owns or can edit the playlist.
