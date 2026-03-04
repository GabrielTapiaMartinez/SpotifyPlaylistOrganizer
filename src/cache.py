import json
import os
from src.getsong_api import get_bpm_key

def load_cache(filepath="data/track_cache.json"):
    """
    Checks if the cache file exists. If it does, read and return the JSON dictionary. 
    If not, return an empty dictionary {}. Ensures the data/ directory exists.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_cache(cache_dict, filepath="data/track_cache.json"):
    """
    Writes the dictionary to the JSON file with an indent of 4 for readability.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(cache_dict, f, indent=4)
    except IOError as e:
        print(f"Error saving cache: {e}")

def process_tracks(tracks, api_key):
    """
    Takes the list of track dictionaries and the GetSongBPM API key.
    Enriches tracks using cache, API, and manual user input as fallback.
    """
    cache_dict = load_cache()
    manual_fix_queue = []
    
    # Step A (Automated Loop)
    print("Enriching tracks (automated)...")
    for track in tracks:
        uri = track.get('uri')
        if not uri:
            continue
            
        if uri in cache_dict:
            # Use cached data
            track.update(cache_dict[uri])
        else:
            # Call API
            print(f"Looking up: {track['name']} by {track['artist']}...")
            data = get_bpm_key(api_key, track['name'], track['artist'])
            
            if data:
                track.update(data)
                cache_dict[uri] = data
            else:
                manual_fix_queue.append(track)
                
    # Step B (Manual Fallback)
    if manual_fix_queue:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"--- Manual Fallback Required for {len(manual_fix_queue)} tracks ---")
        
        for track in manual_fix_queue:
            print(f"\nMissing data for: {track['name']} by {track['artist']}")
            user_input = input("Enter BPM and Key (e.g., '120 8A') or 's' to skip: ").strip()
            
            if user_input.lower() != 's':
                parts = user_input.split(maxsplit=1)
                if len(parts) >= 1:
                    try:
                        bpm = int(parts[0])
                        key = parts[1] if len(parts) > 1 else None
                        
                        data = {"bpm": bpm, "key": key, "open_key": None}
                        track.update(data)
                        
                        # Save to cache dictionary
                        if track.get('uri'):
                            cache_dict[track['uri']] = data
                            
                    except ValueError:
                        print(f"Invalid BPM format for '{parts[0]}'. Skipping manual entry.")
    
    # Final save
    save_cache(cache_dict)
    
    return tracks
