import csv
import dataclasses
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))

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
    popularity: int = 50
    release_decade: str = ""
    secondary_moods: str = ""
    language: str = "english"
    explicit: bool = False

    def __post_init__(self):
        self.energy = _clamp01(self.energy)
        self.valence = _clamp01(self.valence)
        self.danceability = _clamp01(self.danceability)
        self.acousticness = _clamp01(self.acousticness)
        self.popularity = max(0, min(100, self.popularity))

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
    secondary_mood: Optional[str] = None
    preferred_decade: Optional[str] = None
    preferred_language: Optional[str] = None
    min_popularity: Optional[int] = None
    avoid_explicit: bool = False

    def __post_init__(self):
        self.target_energy = _clamp01(self.target_energy)
        if self.min_popularity is not None:
            self.min_popularity = max(0, min(100, self.min_popularity))

    def to_prefs_dict(self) -> Dict:
        """Converts to the plain-dict shape expected by score_song/recommend_songs."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "likes_acoustic": self.likes_acoustic,
            "secondary_mood": self.secondary_mood,
            "preferred_decade": self.preferred_decade,
            "preferred_language": self.preferred_language,
            "min_popularity": self.min_popularity,
            "avoid_explicit": self.avoid_explicit,
        }

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py

    Wraps the dict-based score_song/recommend_songs functions so there is a
    single source of truth for scoring - this class just converts to/from
    dataclasses at the boundary.
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        k = max(k, 0)
        song_dicts = [dataclasses.asdict(song) for song in self.songs]
        ranked = recommend_songs(user.to_prefs_dict(), song_dicts, k=k)
        songs_by_id = {song.id: song for song in self.songs}
        return [songs_by_id[song_dict["id"]] for song_dict, _score, _reasons in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _score, reasons = score_song(user.to_prefs_dict(), dataclasses.asdict(song))
        return "; ".join(reasons) if reasons else "No matching preferences found."

INT_FIELDS = {"id", "tempo_bpm", "popularity"}
FLOAT_FIELDS = {"energy", "valence", "danceability", "acousticness"}
BOOL_FIELDS = {"explicit"}

def load_songs(csv_path: str) -> List[Dict]:
    """Reads a songs CSV into a list of dicts, converting numeric/boolean fields."""
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in INT_FIELDS:
                row[field] = int(row[field])
            for field in FLOAT_FIELDS:
                row[field] = float(row[field])
            for field in BOOL_FIELDS:
                row[field] = row[field].strip().lower() == "true"
            songs.append(row)
    return songs

# Default weight for each scoring factor. Concrete strategies override a
# subset of these to shift emphasis toward genre, mood, or energy.
DEFAULT_WEIGHTS = {
    "mood": 2.0,
    "genre": 1.0,
    "energy": 1.5,
    "acoustic": 1.0,
    "secondary_mood": 1.0,
    "decade": 0.5,
    "language": 0.5,
    "popularity": 1.0,
    "explicit_penalty": 2.0,
}

class ScoringStrategy(ABC):
    """
    Strategy pattern: every concrete strategy scores a song the same way
    (same rules, same reasons) but with a different weight per factor, so
    swapping strategies changes *what the recommender emphasizes* without
    touching recommend_songs or main.py.
    """
    name = "base"
    weights: Dict[str, float] = DEFAULT_WEIGHTS

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        w = self.weights

        def normalize(value):
            return value.strip().lower() if isinstance(value, str) else value

        if normalize(song["mood"]) == normalize(user_prefs.get("mood")):
            score += w["mood"]
            reasons.append(f"Mood match: {song['mood']} (+{w['mood']:.2f})")

        if normalize(song["genre"]) == normalize(user_prefs.get("genre")):
            score += w["genre"]
            reasons.append(f"Genre match: {song['genre']} (+{w['genre']:.2f})")

        target_energy = user_prefs.get("energy")
        if target_energy is not None:
            target_energy = _clamp01(target_energy)
            song_energy = _clamp01(song["energy"])
            energy_points = w["energy"] * (1 - abs(song_energy - target_energy))
            score += energy_points
            reasons.append(f"Energy close to target {target_energy} (+{energy_points:.2f})")

        if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.6:
            score += w["acoustic"]
            reasons.append(f"Acoustic bonus (+{w['acoustic']:.2f})")

        secondary_mood = user_prefs.get("secondary_mood")
        song_secondary_moods = [normalize(m) for m in song["secondary_moods"].split("|")]
        if secondary_mood and normalize(secondary_mood) in song_secondary_moods:
            score += w["secondary_mood"]
            reasons.append(f"Secondary mood match: {secondary_mood} (+{w['secondary_mood']:.2f})")

        preferred_decade = user_prefs.get("preferred_decade")
        if preferred_decade and normalize(song["release_decade"]) == normalize(preferred_decade):
            score += w["decade"]
            reasons.append(f"Release decade match: {preferred_decade} (+{w['decade']:.2f})")

        preferred_language = user_prefs.get("preferred_language")
        if preferred_language and normalize(song["language"]) == normalize(preferred_language):
            score += w["language"]
            reasons.append(f"Language match: {preferred_language} (+{w['language']:.2f})")

        min_popularity = user_prefs.get("min_popularity")
        if min_popularity is not None and song["popularity"] >= min_popularity:
            popularity_points = w["popularity"] * (song["popularity"] / 100)
            score += popularity_points
            reasons.append(f"Popularity bonus: {song['popularity']} (+{popularity_points:.2f})")

        if user_prefs.get("avoid_explicit") and song["explicit"]:
            score -= w["explicit_penalty"]
            reasons.append(f"Explicit content penalty (-{w['explicit_penalty']:.2f})")

        return score, reasons

class BalancedStrategy(ScoringStrategy):
    """The original Algorithm Recipe weights - no single factor dominates."""
    name = "balanced"
    weights = DEFAULT_WEIGHTS

class GenreFirstStrategy(ScoringStrategy):
    """Genre match matters most; mood and energy take a back seat."""
    name = "genre-first"
    weights = {**DEFAULT_WEIGHTS, "genre": 3.0, "mood": 1.0, "energy": 1.0}

class MoodFirstStrategy(ScoringStrategy):
    """Mood and secondary mood tags matter most; genre barely counts."""
    name = "mood-first"
    weights = {**DEFAULT_WEIGHTS, "mood": 4.0, "secondary_mood": 2.0, "genre": 0.5, "energy": 1.0}

class EnergyFocusedStrategy(ScoringStrategy):
    """Matching the target energy level matters most."""
    name = "energy-focused"
    weights = {**DEFAULT_WEIGHTS, "energy": 4.0, "mood": 1.0, "genre": 0.5}

# Registry so callers (e.g. main.py) can look strategies up by name.
STRATEGIES: Dict[str, ScoringStrategy] = {
    strategy.name: strategy
    for strategy in (
        BalancedStrategy(),
        GenreFirstStrategy(),
        MoodFirstStrategy(),
        EnergyFocusedStrategy(),
    )
}

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a song using the default (balanced) strategy, returning (score, reasons)."""
    return STRATEGIES["balanced"].score(user_prefs, song)

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    strategy: Optional[ScoringStrategy] = None,
    artist_penalty: float = 1.0,
    genre_penalty: float = 0.5,
) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song with the given strategy (balanced by default), then picks
    the top k one at a time. Each time a song is picked, later songs by the same
    artist or genre take a growing penalty, so the results don't fill up with
    near-duplicates just because one artist/genre scored well.
    Set artist_penalty=0 and genre_penalty=0 to disable and get raw top-k by score.
    """
    k = max(k, 0)
    strategy = strategy or STRATEGIES["balanced"]
    remaining = [
        (song, *strategy.score(user_prefs, song))
        for song in songs
    ]
    remaining.sort(key=lambda entry: entry[1], reverse=True)

    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    results = []

    while remaining and len(results) < k:
        def diversity_penalty(entry):
            song = entry[0]
            return (
                artist_penalty * artist_counts.get(song["artist"], 0)
                + genre_penalty * genre_counts.get(song["genre"], 0)
            )

        best = max(remaining, key=lambda entry: entry[1] - diversity_penalty(entry))
        remaining.remove(best)

        song, score, reasons = best
        penalty = diversity_penalty(best)
        final_reasons = list(reasons)
        if penalty > 0:
            final_reasons.append(f"Diversity penalty for repeated artist/genre (-{penalty:.2f})")

        results.append((song, score - penalty, "; ".join(final_reasons)))
        artist_counts[song["artist"]] = artist_counts.get(song["artist"], 0) + 1
        genre_counts[song["genre"]] = genre_counts.get(song["genre"], 0) + 1

    return results
