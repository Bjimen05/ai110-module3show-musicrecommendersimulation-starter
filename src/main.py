"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys
import textwrap

from tabulate import tabulate

from recommender import load_songs, recommend_songs, STRATEGIES


def main() -> None:
    # Pick a ranking strategy from the command line, e.g.:
    #   python -m src.main mood-first
    # Falls back to "balanced" if no name is given.
    strategy_name = sys.argv[1] if len(sys.argv) > 1 else "balanced"
    strategy = STRATEGIES.get(strategy_name)
    if strategy is None:
        print(f"Unknown strategy '{strategy_name}'. Available: {', '.join(STRATEGIES)}")
        return

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Ranking strategy: {strategy.name}")

    # Sample user preference profiles
    user_prefs_list = [
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        {"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True},
        {"genre": "metal", "mood": "angry", "energy": 0.95},
    ]

    for user_prefs in user_prefs_list:
        recommendations = recommend_songs(user_prefs, songs, k=5, strategy=strategy)

        print("\nUser Profile")
        print("-" * 40)
        print(f"Genre: {user_prefs['genre']}")
        print(f"Mood: {user_prefs['mood']}")
        print(f"Energy: {user_prefs['energy']}")

        print("\nTop Recommendations")
        table_rows = []
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            reasons = "\n".join(
                textwrap.fill(f"- {reason}", width=40)
                for reason in explanation.split("; ")
            )
            table_rows.append([rank, song["title"], song["artist"], f"{score:.2f}", reasons])

        print(tabulate(
            table_rows,
            headers=["#", "Title", "Artist", "Score", "Reasons"],
            tablefmt="grid",
        ))
        print()


if __name__ == "__main__":
    main()
