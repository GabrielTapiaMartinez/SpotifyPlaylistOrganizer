import os
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_auth_client():
    """
    Reads SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI
    from the environment variables and returns an authenticated `spotipy.Spotify`
    client with the required scopes for playlist modification.
    """
    scope = "playlist-read-private playlist-modify-public playlist-modify-private"
    
    auth_manager = SpotifyOAuth(
        client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
        scope=scope
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def extract_playlist_id(url):
    """
    Takes a standard Spotify playlist URL string and returns just the alphanumeric playlist ID.
    Example URL: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=123
    """
    if not url:
        return None
        
    match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    
    # Fallback to returning the url if no slashes exist, assuming it might already be an ID
    if '/' not in url and '?' not in url:
        return url
        
    return None

def get_playlist_tracks(sp, playlist_id):
    results = []
    
    try:
        # Using playlist_items instead of playlist_tracks for better compatibility
        response = sp.playlist_items(playlist_id)
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
        return results

    while response:
        for item in response.get('items', []):
            # Check 'track' first (legacy), then 'item' (modern/episodes)
            track_data = item.get('track') or item.get('item')
            
            # Defensive check: skip if both are missing or if it's not a track
            if not track_data or track_data.get('type') != 'track':
                continue
            
            # Filter out local files
            if track_data.get('is_local'):
                continue
                
            uri = track_data.get('uri')
            name = track_data.get('name')
            artists = track_data.get('artists')
            
            if uri and name and artists:
                primary_artist_name = artists[0].get('name', 'Unknown Artist')
                results.append({
                    "uri": uri,
                    "name": name,
                    "artist": primary_artist_name
                })
        
        # Standard Spotipy pagination
        if response.get('next'):
            response = sp.next(response)
        else:
            response = None
            
    return results

def update_playlist(sp, playlist_id, sorted_uris):
    """
    Replaces the current playlist items with the provided list of sorted track URIs.
    Handles the 100 items per request limit.
    """
    if not sorted_uris:
        try:
            sp.playlist_replace_items(playlist_id, [])
        except Exception as e:
            print(f"Error clearing playlist (empty URI list provided): {e}")
        return

    # The Spotify API allows a maximum of 100 items for replacement/addition per request
    chunk_size = 100
    
    # First chunk replaces the entire existing playlist
    first_chunk = sorted_uris[:chunk_size]
    try:
        sp.playlist_replace_items(playlist_id, first_chunk)
    except Exception as e:
        print(f"Error replacing playlist items: {e}")
        return
        
    # Any remaining URIs must be added in subsequent requests of up to 100 items each
    for i in range(chunk_size, len(sorted_uris), chunk_size):
        chunk = sorted_uris[i:i + chunk_size]
        try:
            sp.playlist_add_items(playlist_id, chunk)
        except Exception as e:
            print(f"Error adding playlist items at chunk index {i}: {e}")
            break
