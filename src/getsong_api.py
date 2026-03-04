import time
import requests
import re

def clean_title(title):
    # Removes (feat. ...), - Remastered, etc.
    return re.sub(r'\(.*?\)|- .*', '', title).strip()

def get_bpm_key(api_key, song_title, artist_name):
    time.sleep(1.2) # Rate limit
    url = "https://api.getsong.co/search/"
    
    # Try 1: Search for the song specifically
    display_title = clean_title(song_title)
    params = {
        'api_key': api_key,
        'type': 'song',
        'lookup': display_title,
        'limit': 5 # Get a few results to check for the right artist
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # The API returns results in a 'search' list
        results = data.get('search', [])
        
        # FIX: Ensure results is actually a list and not an empty dict/string
        if not isinstance(results, list) or len(results) == 0:
            return None

        best_match = None
        for res in results:
            if not isinstance(res, dict):
                continue 
            
            res_artist = res.get('artist', {}).get('name', '').lower()
            if artist_name.lower() in res_artist or res_artist in artist_name.lower():
                best_match = res
                break
        
        # Safe to use [0] now because we verified it's a populated list
        if not best_match:
            best_match = results[0]

        raw_tempo = best_match.get('tempo')
        # Ensure tempo is a valid number > 0
        try:
            bpm = int(float(raw_tempo))
        except (TypeError, ValueError):
            bpm = 0

        if bpm > 0:
            return {
                "bpm": bpm,
                "key": best_match.get('key_of'),
                "open_key": best_match.get('open_key')
            }
            
    except Exception as e:
        # Use repr(e) to see the EXACT error type during debugging
        print(f"DEBUG: Error looking up {song_title}: {repr(e)}")
        
    return None
