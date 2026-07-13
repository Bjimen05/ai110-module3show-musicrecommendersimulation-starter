"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Sample user preference profiles
    user_prefs_list = [
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        {"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True},
        {"genre": "metal", "mood": "angry", "energy": 0.95},
    ]

    for user_prefs in user_prefs_list:
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\nUser Profile")
        print("-" * 40)
        print(f"Genre: {user_prefs['genre']}")
        print(f"Mood: {user_prefs['mood']}")
        print(f"Energy: {user_prefs['energy']}")

        print("\nTop Recommendations")
        print("=" * 40)
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"\n{rank}. {song['title']} - {song['artist']}")
            print(f"   Score: {score:.2f}")
            print("   Because:")
            for reason in explanation.split("; "):
                print(f"     - {reason}")
        print()


if __name__ == "__main__":
    main()
