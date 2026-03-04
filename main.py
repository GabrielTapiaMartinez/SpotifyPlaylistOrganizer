import os
import sys
from dotenv import load_dotenv

# Import our custom modules
from src.spotify_api import get_auth_client, extract_playlist_id, get_playlist_tracks, update_playlist
from src.cache import process_tracks
from src.sorter import sort_playlist

def main():
    # 1. Setup and Authentication
    load_dotenv()
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    getsong_api_key = os.getenv('GETSONGBPM_API_KEY')

    if not spotify_client_id or not getsong_api_key:
        print("Error: Missing API keys in .env file.")
        sys.exit(1)

    print("Authenticating with Spotify...")
    sp = get_auth_client()

    # 2. User Input
    print("\n" + "="*50)
    print(" HARMONIC PLAYLIST ORGANIZER ")
    print("="*50)
    playlist_url = input("Paste the Spotify Playlist URL to organize: ").strip()
    playlist_id = extract_playlist_id(playlist_url)

    if not playlist_id:
        print("Error: Could not extract Playlist ID. Check the URL.")
        sys.exit(1)

    # 3. Ingestion
    print(f"\nFetching tracks for Playlist ID: {playlist_id}...")
    tracks = get_playlist_tracks(sp, playlist_id)
    if not tracks:
        print("No tracks found or playlist is private/empty.")
        sys.exit(1)
    print(f"Found {len(tracks)} tracks.")

    # 4. Enrichment (GetSongBPM + Cache + Manual Fallback)
    print("\nStarting track enrichment (BPM & Key)...")
    enriched_tracks = process_tracks(tracks, getsong_api_key)

    # 5. Sorting Engine
    print("\nCalculating optimal harmonic path...")
    sorted_tracks = sort_playlist(enriched_tracks)
    
    if not sorted_tracks:
        print("Error: Not enough valid tracks to sort.")
        sys.exit(1)
        
    print(f"Successfully sorted {len(sorted_tracks)} tracks.")

    # Print the preview
    print("\n--- Optimized Playlist Preview ---")
    for i, t in enumerate(sorted_tracks[:15]):
        key_disp = t.get('key', 'Unknown')
        print(f"{i+1}. {t['name']} - {t.get('bpm')} BPM | Key: {key_disp}")
    if len(sorted_tracks) > 15:
        print(f"... and {len(sorted_tracks) - 15} more.")

    # 6. Execution (Write to Spotify)
    print("\n" + "="*50)
    confirm = input("Overwrite the Spotify playlist with this new order? (y/n): ").strip().lower()
    
    if confirm == 'y':
        print("\nUpdating Spotify playlist...")
        sorted_uris = [t['uri'] for t in sorted_tracks if t.get('uri')]
        update_playlist(sp, playlist_id, sorted_uris)
        print("Success! Your playlist has been harmonically organized.")
    else:
        print("\nOperation cancelled. No changes made to Spotify.")

if __name__ == "__main__":
    main()