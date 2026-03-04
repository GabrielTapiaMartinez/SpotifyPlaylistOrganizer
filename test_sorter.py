from src.sorter import sort_playlist

tracks = [
    {"name": "Track A", "bpm": 120, "key": "8A"},
    {"name": "Track B", "bpm": 122, "key": "8A"},
    {"name": "Track C", "bpm": 128, "key": "10A"}
]

sorted_tracks = sort_playlist(tracks)
for t in sorted_tracks:
    print(f"{t['name']} - {t['bpm']} BPM, {t['key']}")
