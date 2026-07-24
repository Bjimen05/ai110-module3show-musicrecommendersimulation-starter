# 🎵 Music Recommender Simulation

A content-based music recommendation engine built from scratch in Python — no external ML libraries, just an explicit, explainable scoring model over song and user-taste features.

Given a listener's taste profile (genre, mood, target energy, acoustic preference, and more), the system scores every song in a catalog, ranks the top matches, and explains **why** each song was recommended. It supports multiple swappable ranking strategies and a diversity penalty so results don't get dominated by a single artist or genre.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Sample Output](#sample-output)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Adversarial Testing & Robustness](#adversarial-testing--robustness)
- [Design Decisions & Reflection](#design-decisions--reflection)
- [Limitations](#limitations)

---

## Overview

This project simulates how systems like Spotify or YouTube Music turn stated (or inferred) listener preferences into ranked recommendations. It's built around three core ideas:

- **Represent** songs and a user's taste as structured data
- **Score** each song against a user profile using a transparent, weighted rule
- **Explain** every recommendation in plain language, not just a number

**Key features:**

- 🎯 Weighted, multi-factor scoring (mood, genre, energy proximity, acoustic preference, decade, language, popularity, explicit-content filtering)
- 🔀 Four swappable ranking strategies (`balanced`, `genre-first`, `mood-first`, `energy-focused`) via a Strategy pattern
- 🌈 A diversity penalty that prevents one artist or genre from dominating the top-k results
- 🛡️ Input validation and defensive guards (energy clamping, case-insensitive matching, non-negative `k`)
- ✅ Unit tests covering the OOP interface (`Song`, `UserProfile`, `Recommender`)

---

## How It Works

### Data model

| Class | Represents | Key fields |
|---|---|---|
| `Song` | A track and its attributes | `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`, `popularity`, `release_decade`, `secondary_moods`, `language`, `explicit` |
| `UserProfile` | A listener's taste | `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`, `secondary_mood`, `preferred_decade`, `preferred_language`, `min_popularity`, `avoid_explicit` |

### Scoring

Each song earns points for how well it matches the user's profile:

| Signal | Weight (balanced strategy) |
|---|---|
| Mood match | +2.0 |
| Genre match | +1.0 |
| Energy proximity to target | up to +1.5 |
| Acoustic bonus | +1.0 |
| Secondary mood match | +1.0 |
| Release decade match | +0.5 |
| Language match | +0.5 |
| Popularity bonus | up to +1.0 |
| Explicit content (if avoided) | −2.0 |

Every song is scored, sorted highest to lowest, and the top `k` are returned along with a plain-language explanation built from whichever rules fired. A **diversity penalty** grows each time a song by the same artist or genre is picked, so later picks from an over-represented artist/genre are pushed down — keeping the results varied instead of one artist sweeping the list.

Four ranking strategies (`balanced`, `genre-first`, `mood-first`, `energy-focused`) reuse the same scoring rules with different weight emphasis, selectable from the command line.

### Robustness

Earlier iterations of this project had real bugs — worth calling out because finding and fixing them was part of the exercise:

- Exact string matching meant `"Pop"` never matched `"pop"` — fixed with case/whitespace normalization.
- An out-of-range `target_energy` (e.g. `5.0`) could tank an otherwise perfect match — fixed by clamping energy to `[0, 1]`.
- A negative `k` silently returned almost the entire catalog due to Python's slice semantics — fixed by clamping `k` to a non-negative value.

See [Adversarial Testing & Robustness](#adversarial-testing--robustness) for the full writeup, and [`model_card.md`](model_card.md) for a deeper reflection on design tradeoffs and bias.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

   Optionally pick a ranking strategy:

   ```bash
   python -m src.main mood-first
   ```

   Available strategies: `balanced` (default), `genre-first`, `mood-first`, `energy-focused`.

---

## Sample Output

```
Loading songs from data/songs.csv...
Loaded songs: 30
Ranking strategy: balanced

User Profile
----------------------------------------
Genre: pop
Mood: happy
Energy: 0.8

Top Recommendations
+-----+-------------------+---------------+---------+------------------------------------------+
|   # | Title             | Artist        |   Score | Reasons                                   |
+=====+===================+===============+=========+============================================+
|   1 | Sunrise City      | Neon Echo     |    4.47 | - Mood match: happy (+2.00)                |
|     |                   |               |         | - Genre match: pop (+1.00)                 |
|     |                   |               |         | - Energy close to target 0.8 (+1.47)       |
+-----+-------------------+---------------+---------+------------------------------------------+
|   2 | Rooftop Lights    | Indigo Parade |    3.44 | - Mood match: happy (+2.00)                |
|     |                   |               |         | - Energy close to target 0.8 (+1.44)       |
+-----+-------------------+---------------+---------+------------------------------------------+
|   3 | Pixel Crush       | NOVA7         |    3.38 | - Mood match: happy (+2.00)                |
|     |                   |               |         | - Energy close to target 0.8 (+1.38)       |
+-----+-------------------+---------------+---------+------------------------------------------+
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Testing

Run the test suite with:

```bash
pytest
```

Tests in [`tests/test_recommender.py`](tests/test_recommender.py) exercise the OOP interface end-to-end (`Recommender.recommend`, `Recommender.explain_recommendation`) — not a separate mock path — so a passing suite reflects the same code that runs in `main.py`.

---

## Project Structure

```
├── src/
│   ├── main.py          # CLI entry point — loads data, runs sample profiles, prints results
│   └── recommender.py   # Song/UserProfile/Recommender classes + scoring & ranking logic
├── tests/
│   └── test_recommender.py
├── data/
│   └── songs.csv         # 30-song catalog with genre, mood, energy, and other attributes
├── model_card.md          # Design rationale, evaluation, limitations, and reflection
└── requirements.txt
```

---

## Adversarial Testing & Robustness

To stress-test the scoring logic, I ran the recommender against deliberately adversarial user profiles and inspected the output. This surfaced real issues, all since fixed in the current implementation:

| Test | Input | Original behavior | Fix |
|---|---|---|---|
| Out-of-range energy | `energy: 5.0` | Score went deeply negative even for a mood+genre "perfect match" | Energy clamped to `[0, 1]` before scoring |
| Non-numeric energy | `energy: "high"` | Crashed with a `TypeError` | N/A — caught via type-safe profile construction |
| Negative `k` | `k=-1` | Returned 29 of 30 songs due to Python's negative-index slicing | `k` clamped to `max(k, 0)` |
| Case/whitespace mismatch | `genre: "Pop"`, `mood: " happy"` | Genre/mood points silently lost, score dropped from 4.47 to 1.47 | Case-insensitive, whitespace-trimmed string comparison |
| Empty profile | `{}` | Every song scored 0.0 — "ranking" was just CSV load order | Documented as an expected no-signal case |

Full before/after detail and reasoning lives in [`model_card.md`](model_card.md#7-evaluation).

---

## Design Decisions & Reflection

Building this made it clear that a recommender is, underneath, just a scoring formula with weights someone chose — there's no "understanding" of music, only numbers being compared. Small changes to those weights (like doubling the energy weight or halving the genre weight) noticeably shifted which songs won, which drove home how much a system's apparent "taste" depends on decisions made by the builder, not the user.

It also surfaced where bias can hide in a system like this: through exact-match rules (typos or casing silently losing points), through which features get scored at all (valence and danceability are captured in the data but currently unused), and through a thin catalog where niche genres/moods have only one representative song. None of that looks like "bias" in the code — it looks like ordinary scoring — which is exactly what makes it easy to miss.

Full reflection, evaluation methodology, and future-work ideas are in [`model_card.md`](model_card.md).

---

## Limitations

- Small catalog (30 songs); most genres/moods are singletons, which limits meaningful ranking within a category
- No use of listening history, skips, or collaborative signals — purely content-based on stated preferences
- Doesn't consider lyrics or audio beyond the provided tabular features
- Mood carries the most weight by default, which can outweigh a better overall fit in the `balanced` strategy
