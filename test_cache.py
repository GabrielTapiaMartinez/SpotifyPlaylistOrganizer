import os
from dotenv import load_dotenv
from src.spotify_api import get_auth_client, extract_playlist_id, get_playlist_tracks
from src.cache import process_tracks

def main():
    load_dotenv()
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    getsong_api_key = os.getenv('GETSONGBPM_API_KEY')
    
    sp = get_auth_client()
    playlist_id = extract_playlist_id("https://open.spotify.com/playlist/7EqEd3XHzYOVA4sXxbwKjs")
    
    tracks = get_playlist_tracks(sp, playlist_id)
    
    enriched_tracks = process_tracks(tracks[:5], getsong_api_key)
    print("\n--- Final Test Results ---")
    for t in enriched_tracks:
        status = "Enriched" if 'bpm' in t else "Missing Data"
        print(f"[{status}] {t['name']} - {t.get('bpm', '??')} BPM")

if __name__ == "__main__":
    main()
