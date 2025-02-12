import os
import pickle
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OAuth scopes required for full YouTube Data access:
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_service():
    """
    Creates and returns an authorized YouTube API client using OAuth.
    """
    creds = None
    # token.pickle stores the user's credentials locally
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token_file:
            creds = pickle.load(token_file)

    # If no (valid) credentials available, prompt user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.pickle", "wb") as token_file:
            pickle.dump(creds, token_file)

    return build("youtube", "v3", credentials=creds)

def get_playlist_items(youtube, playlist_id):
    """
    Fetch all video IDs from the given playlist (up to any size).
    Returns a list of video IDs.
    """
    video_ids = []
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )

    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            resource = item["snippet"]["resourceId"]
            if resource["kind"] == "youtube#video":
                video_ids.append(resource["videoId"])
        request = youtube.playlistItems().list_next(request, response)

    return video_ids

def create_new_playlist(youtube, title, description=""):
    """
    Create a new playlist with a given title and optional description.
    Returns the new playlist ID.
    """
    request_body = {
        "snippet": {
            "title": title,
            "description": description
        },
        "status": {
            "privacyStatus": "private"  # could be "public" or "unlisted"
        }
    }

    response = youtube.playlists().insert(
        part="snippet,status",
        body=request_body
    ).execute()

    return response["id"]

def add_videos_to_playlist(youtube, playlist_id, video_ids):
    """
    Add a list of video IDs to a specified playlist, in chunks.
    Includes basic exponential backoff if an insertion fails.
    """
    chunk_size = 50
    for start_index in range(0, len(video_ids), chunk_size):
        chunk = video_ids[start_index:start_index + chunk_size]
        print(f"Adding chunk {start_index} - {start_index + len(chunk) - 1} "
              f"({len(chunk)} videos) to playlist {playlist_id}...")

        for vid in chunk:
            attempt = 1
            max_attempts = 5
            sleep_time = 2  # initial backoff seconds

            while attempt <= max_attempts:
                try:
                    request_body = {
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": vid
                            }
                        }
                    }
                    youtube.playlistItems().insert(
                        part="snippet",
                        body=request_body
                    ).execute()
                    print(f"  Added video {vid}")
                    break  # insertion succeeded, go to next video
                except HttpError as e:
                    print(f"  Error inserting {vid} (attempt {attempt}/{max_attempts}): {e}")
                    if attempt == max_attempts:
                        print(f"  Failed to insert {vid} after {max_attempts} attempts. Skipping.")
                    else:
                        # Wait, then try again with exponential backoff
                        time.sleep(sleep_time)
                        sleep_time *= 2
                attempt += 1

        # Short pause between each chunk
        time.sleep(5)
    print(f"Finished adding {len(video_ids)} videos to playlist {playlist_id}.")

def main():
    # The original playlist ID (YouTube/YouTube Music)
    # e.g. from: https://music.youtube.com/playlist?list=PLxxxx
    # Use whatever your playlist ID is. Make sure it's the same account that owns it.
    original_playlist_id = "PL2dp0NZUSY7OCpzZj8SRaLXcHR2MoA5vX"  # <-- CHANGE THIS

    # 1. Authorize and get the YouTube service
    youtube = get_youtube_service()

    # 2. Fetch all video IDs from the original playlist
    video_ids = get_playlist_items(youtube, original_playlist_id)
    total_videos = len(video_ids)
    print(f"Total videos found: {total_videos}")

    if total_videos == 0:
        print("No videos found in the playlist. Exiting...")
        return

    # 3. Split the list into two halves (here you can adjust the split logic - depending how many videos your playlist has, should be about ~200)
    midpoint = total_videos // 2
    first_half = video_ids[:midpoint]
    second_half = video_ids[midpoint:]

    # 4. Create two new playlists
    playlist1_id = create_new_playlist(youtube, "My Playlist - Part 1", "First half")
    playlist2_id = create_new_playlist(youtube, "My Playlist - Part 2", "Second half")

    print(f"New Playlist Part 1 ID: {playlist1_id}")
    print(f"New Playlist Part 2 ID: {playlist2_id}")

    # 5. Add first half of videos to the first new playlist
    add_videos_to_playlist(youtube, playlist1_id, first_half)

    # 6. Add second half of videos to the second new playlist
    add_videos_to_playlist(youtube, playlist2_id, second_half)

    print("All done!")

if __name__ == "__main__":
    main()
