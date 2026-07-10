import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

INT_FIELDS = {"id", "tempo_bpm"}
FLOAT_FIELDS = {"energy", "valence", "danceability", "acousticness"}

def load_songs(csv_path: str) -> List[Dict]:
    """Reads a songs CSV into a list of dicts, converting numeric fields to int/float."""
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in INT_FIELDS:
                row[field] = int(row[field])
            for field in FLOAT_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a song against user preferences using the weighted Algorithm Recipe, returning (score, reasons)."""
    score = 0.0
    reasons = []

    if song["mood"] == user_prefs.get("mood"):
        score += 2.0
        reasons.append(f"Mood match: {song['mood']} (+2.0)")

    if song["genre"] == user_prefs.get("genre"):
        score += 1.0
        reasons.append(f"Genre match: {song['genre']} (+1.0)")

    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        energy_points = 1.5 * (1 - abs(song["energy"] - target_energy))
        score += energy_points
        reasons.append(f"Energy close to target {target_energy} (+{energy_points:.2f})")

    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.6:
        score += 1.0
        reasons.append("Acoustic bonus (+1.0)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song, sorts by score descending, and returns the top k as (song, score, explanation)."""
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]
    scored.sort(key=lambda entry: entry[1], reverse=True)

    return [
        (song, score, "; ".join(reasons))
        for song, score, reasons in scored[:k]
    ]
