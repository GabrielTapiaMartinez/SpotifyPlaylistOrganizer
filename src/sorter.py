import math

CAMELOT_WHEEL = {
    "B": "1B", "G#m": "1A", "Abm": "1A",
    "F#": "2B", "Gb": "2B", "D#m": "2A", "Ebm": "2A",
    "Db": "3B", "C#": "3B", "Bbm": "3A", "A#m": "3A",
    "Ab": "4B", "G#": "4B", "Fm": "4A",
    "Eb": "5B", "D#": "5B", "Cm": "5A",
    "Bb": "6B", "A#": "6B", "Gm": "6A",
    "F": "7B", "Dm": "7A",
    "C": "8B", "Am": "8A",
    "G": "9B", "Em": "9A",
    "D": "10B", "Bm": "10A",
    "A": "11B", "F#m": "11A", "Gbm": "11A",
    "E": "12B", "C#m": "12A", "Dbm": "12A"
}

def normalize_key(key_str):
    """
    Standardizes a given key string by replacing sharp and flat 
    unicode symbols with standard # and b characters for dictionary lookup.
    """
    if not key_str:
        return None
        
    normalized = key_str.replace('♯', '#').replace('♭', 'b')
    return CAMELOT_WHEEL.get(normalized)

def parse_camelot(camelot_str):
    """
    Splits a Camelot key string (e.g. '8A') into its integer number and letter.
    """
    if not camelot_str:
        return None, None
    try:
        num = int(camelot_str[:-1])
        letter = camelot_str[-1].upper()
        return num, letter
    except (ValueError, IndexError):
        return None, None

def get_camelot_distance(num1, num2):
    """
    Calculates the shortest distance around the 1-12 Camelot wheel.
    """
    diff = abs(num1 - num2)
    return min(diff, 12 - diff)

def get_bpm_variance(target_bpm, current_bpm):
    """
    Calculates the BPM variance as a percentage relative to the current BPM.
    """
    if current_bpm == 0:
        return float('inf')
    return abs(target_bpm - current_bpm) / current_bpm

def evaluate_tracks(current_track, candidate_track):
    """
    Evaluates how well a candidate track transitions from the current track.
    Returns a dictionary of metrics if both have valid data, else returns None.
    """
    c_key = normalize_key(current_track.get('key'))
    n_key = normalize_key(candidate_track.get('key'))
    
    if not c_key or not n_key:
        return None
        
    c_num, c_letter = parse_camelot(c_key)
    n_num, n_letter = parse_camelot(n_key)
    
    if c_num is None or n_num is None:
        return None
        
    c_bpm = float(current_track.get('bpm', 0))
    n_bpm = float(candidate_track.get('bpm', 0))
    
    if c_bpm == 0:
        return None
        
    distance = get_camelot_distance(c_num, n_num)
    letter_match = (c_letter == n_letter)
    
    variance = get_bpm_variance(n_bpm, c_bpm)
    
    # Calculate Double/Half BPM variance
    half_bpm_var = get_bpm_variance(n_bpm, c_bpm * 0.5)
    double_bpm_var = get_bpm_variance(n_bpm, c_bpm * 2.0)
    dh_variance = min(half_bpm_var, double_bpm_var)
    
    # Step difference for relative directional shifts (+2, +7)
    # E.g., moving from 8 to 10 is +2. Moving from 12 to 2 is +2.
    steps_up = (n_num - c_num) % 12
    
    return {
        'distance': distance,
        'steps_up': steps_up,
        'letter_match': letter_match,
        'variance': variance,
        'dh_variance': dh_variance,
        'bpm_diff': abs(n_bpm - c_bpm) 
    }

def sort_playlist(tracks):
    """
    Sorts a list of track dictionaries using a DJ-style Tiered Waterfall 
    pathfinding algorithm based on BPM and the Camelot Wheel.
    """
    # 1. Filter out tracks missing 'bpm' or 'key'
    valid_tracks = []
    for track in tracks:
        if track.get('bpm') and track.get('key') and normalize_key(track.get('key')):
            valid_tracks.append(track)
            
    if not valid_tracks:
        return []

    # 2. Start the sorted list with the track that has the lowest base BPM
    valid_tracks.sort(key=lambda x: float(x['bpm']))
    sorted_tracks = [valid_tracks.pop(0)]
    
    # 3. Waterfall Pathfinding loop
    while valid_tracks:
        current_track = sorted_tracks[-1]
        
        # Initialize buckets for tiers
        tier_candidates = {tier: [] for tier in range(1, 7)}
        
        for idx, candidate in enumerate(valid_tracks):
            metrics = evaluate_tracks(current_track, candidate)
            if not metrics:
                continue
                
            dist = metrics['distance']
            steps_up = metrics['steps_up']
            letter_match = metrics['letter_match']
            var = metrics['variance']
            dh_var = metrics['dh_variance']
            bpm_diff = metrics['bpm_diff']
            
            candidate_info = {'idx': idx, 'bpm_diff': bpm_diff}
            
            # Note: We must carefully place each candidate into the FIRST tier it qualifies for.
            # Using elif handles the strict fallback hierarchy.
            
            if dist <= 1 and letter_match and var <= 0.03:
                # Tier 1 (Perfect Flow)
                tier_candidates[1].append(candidate_info)
                
            elif dist <= 1 and letter_match and var <= 0.07:
                # Tier 2 (Tempo Flex)
                tier_candidates[2].append(candidate_info)
                
            elif dist <= 1 and letter_match and dh_var <= 0.02:
                # Tier 3 (Double/Half)
                # For tie-breaking, we recalculate diff to reflect effective BPM
                c_bpm = float(current_track.get('bpm', 0))
                n_bpm = float(candidate.get('bpm', 0))
                half_diff = abs(n_bpm - (c_bpm * 0.5))
                double_diff = abs(n_bpm - (c_bpm * 2.0))
                candidate_info['bpm_diff'] = min(half_diff, double_diff)
                
                tier_candidates[3].append(candidate_info)
                
            elif steps_up == 2 and letter_match and var <= 0.03:
                # Tier 4 (Power-Up)
                tier_candidates[4].append(candidate_info)
                
            elif steps_up == 7 and letter_match and var <= 0.03:
                # Tier 5 (Jaws Drop)
                tier_candidates[5].append(candidate_info)
                
            elif dist == 0 and not letter_match and var <= 0.03:
                # Tier 6 (Mood Flip)
                tier_candidates[6].append(candidate_info)

        # Select the winning candidate
        chosen_idx = None
        
        # Check standard tiers 1-6
        for tier in range(1, 7):
            if tier_candidates[tier]:
                # If multiple candidates pass a tier, pick the one with the smallest BPM diff
                tier_candidates[tier].sort(key=lambda x: x['bpm_diff'])
                chosen_idx = tier_candidates[tier][0]['idx']
                break
                
        # Tier 7 (Tempo Reset Fallback)
        if chosen_idx is None:
            # Ignore key completely. Find the track with absolute closest base BPM
            best_diff = float('inf')
            c_bpm = float(current_track.get('bpm', 0))
            
            for idx, candidate in enumerate(valid_tracks):
                diff = abs(float(candidate.get('bpm', 0)) - c_bpm)
                if diff < best_diff:
                    best_diff = diff
                    chosen_idx = idx
                    
        # Pop the winning candidate and append to our sorted array
        sorted_tracks.append(valid_tracks.pop(chosen_idx))
        
    return sorted_tracks
