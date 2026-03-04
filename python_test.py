import os
from dotenv import load_dotenv
from src.spotify_api import get_auth_client, extract_playlist_id, get_playlist_tracks
from src.getsong_api import get_bpm_key

def main():
    # 1. Load credentials
    load_dotenv()
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    getsong_api_key = os.getenv('GETSONGBPM_API_KEY')

    if not spotify_client_id or not getsong_api_key:
        print("Error: Make sure SPOTIFY_CLIENT_ID and GETSONGBPM_API_KEY are in your .env file.")
        return

    # 2. Setup Spotify Client
    sp = get_auth_client()
    
    # 3. Input Playlist URL (You can hardcode one here for testing)
    playlist_url = input("Paste a Spotify Playlist URL to test: ")
    playlist_id = extract_playlist_id(playlist_url)
    
    if not playlist_id:
        print("Invalid Spotify URL.")
        return

    print(f"\n--- Fetching tracks for Playlist ID: {playlist_id} ---")
    tracks = get_playlist_tracks(sp, playlist_id)
    print(f"Found {len(tracks)} tracks.")

    # 4. Test Enrichment (Limit to first 5 tracks to save time/API quota)
    test_limit = 5
    print(f"\n--- Testing GetSongBPM Enrichment (First {test_limit} tracks) ---")
    
    enriched_tracks = []
    for track in tracks[:test_limit]:
        print(f"Looking up: {track['name']} by {track['artist']}...")
        
        # Call your getsong_api function
        data = get_bpm_key(getsong_api_key, track['name'], track['artist'])
        
        if data:
            track.update(data)
            print(f"  [SUCCESS] BPM: {data['bpm']}, Key: {data['key']}")
        else:
            print(f"  [FAILED] No data found.")
            
        enriched_tracks.append(track)

    print("\n--- Final Test Results ---")
    for t in enriched_tracks:
        status = "Enriched" if 'bpm' in t else "Missing Data"
        print(f"[{status}] {t['name']} - {t.get('bpm', '??')} BPM")

if __name__ == "__main__":
    main()