# Harmonic Spotify Playlist Organizer

This Python tool automatically organizes your Spotify playlists harmonically, ensuring your tracks flow flawlessly like a DJ set. It enriches your playlist tracks with real-time BPM and Key data, and then sorts them using a dynamic Camelot Wheel pathfinding algorithm.

BPM and Key data provided by [GetSongBPM](https://getsongbpm.com).

## Features
- **Spotify Integration:** Fetches and updates playlists seamlessly via the `spotipy` library.
- **GetSongBPM Enrichment:** Pulls in BPM and Key data dynamically. 
- **Local Caching:** Caches API responses to a local JSON file (`data/track_cache.json`) to minimize redundant requests and respect API limits.
- **Manual Fallback:** Prompts you interactively in the terminal to add BPM/Key data if a track isn't found online.
- **Tiered Waterfall Sorter:** Uses a custom DJ sorting algorithm:
  - Perfect flow (Camelot 1 step, BPM variance < 3%)
  - Power-Ups (+2 steps)
  - Jaws Drops (+7 steps)
  - Mood Flips (A<->B letter flips)
  - Double/Half-time BPM matching

## Setup
1. Create a virtual environment and install the dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the root directory and add your API keys:
   ```env
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   GETSONGBPM_API_KEY=your_api_key
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage
Simply run the script and paste the URL of your target Spotify Playlist when prompted. The tool will preview the optimal harmonic path and ask for confirmation before it overwrites your actual Spotify playlist with the sorted data.
