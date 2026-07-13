# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version scores a small catalog of songs against a user's stated taste (genre, mood, energy, acoustic preference, plus popularity, decade, language, and secondary mood) and returns the top matches with a plain-language explanation for each. It supports multiple ranking strategies (balanced, genre-first, mood-first, energy-focused) and applies a diversity penalty so results don't get dominated by one artist or genre.

---

## How The System Works

Explain your design in plain language.

*Spotify and YouTube use song features like genre, mood, tempo, energy and user history like plays, likes and skips, to learn listener's preferences, as well as score possible songs, and rank the best matches at the top of the recommendation list.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo

  *Each song use mood, genre, valence, energy, tempo, danceability and acousticness in my system.

- What information does your `UserProfile` store

  *It store what their favorite genre, mood, target energy level, whether user prefer acoustic songs

- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

  *Each song is scored against the user's profile using the weighted sum of the 5 features, using a proximity formula so songs closest to the user's preference score highest. Mood matches +2 pts, Genre matches 1+ pts, Energy close to user's target up to 1.5+ pts, Acoustic 1+ pts.

  *After scoring every songs in the catalog with score_song(), the recommender collect all song and score pairs, sort them in descending order, and return the top-k results. User get the k songs with the highest alignment to their profile and an explanation why one song matched

You can include a simple diagram or bullet list if helpful.

https://claude.ai/code/artifact/4e2af624-fd93-4bd4-996c-c5a74bd8a6d0

Potential Biases

  *Mood has the biggest influence, so songs with right mood may rank higher even if they're different genre. Also users that don't like acoustic songs aren't penalized, so acoustic songs may still appear.
---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
Loading songs from data/songs.csv...
Loaded songs: 30

User Profile
----------------------------------------
Genre: pop
Mood: happy
Energy: 0.8

Top Recommendations
========================================

1. Sunrise City - Neon Echo
   Score: 4.47
   Because:
     - Mood match: happy (+2.0)
     - Genre match: pop (+1.0)
     - Energy close to target 0.8 (+1.47)

2. Rooftop Lights - Indigo Parade
   Score: 3.44
   Because:
     - Mood match: happy (+2.0)
     - Energy close to target 0.8 (+1.44)

3. Pixel Crush - NOVA7
   Score: 3.38
   Because:
     - Mood match: happy (+2.0)
     - Energy close to target 0.8 (+1.38)

4. Gym Hero - Max Pulse
   Score: 2.30
   Because:
     - Genre match: pop (+1.0)
     - Energy close to target 0.8 (+1.30)

5. Groove Tunnel - Funkspot
   Score: 1.47
   Because:
     - Energy close to target 0.8 (+1.47)

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Adversarial / Edge Case Testing

To stress-test `score_song` and `recommend_songs`, I ran the recommender against several adversarial user profiles and observed the top 5 results (or fewer, where noted) from the terminal.

### Adversarial 1: Out-of-range `target_energy`

Profile: `{"genre": "metal", "mood": "angry", "energy": 5.0}`

The formula `1.5 * (1 - abs(song["energy"] - target_energy))` assumes energy stays in `[0, 1]` and is never clamped, so an out-of-range target drags every score deeply negative — even the "perfect" mood+genre match.

```
============================================================
Adversarial 1: Out-of-range target_energy
Profile: {'genre': 'metal', 'mood': 'angry', 'energy': 5.0}
----------------------------------------
Returned 5 results (k=5)

Top Recommendations
========================================
1. Iron Curtain - Razorback
   Score: -1.54
   Because:
     - Mood match: angry (+2.0)
     - Genre match: metal (+1.0)
     - Energy close to target 5.0 (+-4.54)

2. Static Truth - The Wrecks
   Score: -2.67
   Because:
     - Mood match: angry (+2.0)
     - Energy close to target 5.0 (+-4.67)

3. Drop Into Light - AXON
   Score: -4.56
   Because:
     - Energy close to target 5.0 (+-4.56)

4. Bass Reactor - Coldwire
   Score: -4.59
   Because:
     - Energy close to target 5.0 (+-4.59)

5. Gym Hero - Max Pulse
   Score: -4.61
   Because:
     - Energy close to target 5.0 (+-4.61)
```

### Adversarial 2: Non-numeric `energy` (type crash)

Profile: `{"genre": "pop", "mood": "happy", "energy": "high"}`

`user_prefs` is an unvalidated dict, so a non-numeric energy value crashes scoring entirely instead of degrading gracefully.

```
============================================================
Adversarial 2: Non-numeric energy (type crash)
Profile: {'genre': 'pop', 'mood': 'happy', 'energy': 'high'}
----------------------------------------
CRASHED: TypeError: unsupported operand type(s) for -: 'float' and 'str'
```

### Adversarial 3: Negative `k` (k=-1)

Profile: `{"genre": "pop", "mood": "happy", "energy": 0.8}`, called with `k=-1`

Python's slice `scored[:-1]` drops only the last element rather than returning zero results, so a negative `k` silently returns nearly the entire catalog (29 of 30 songs) instead of an empty list.

```
============================================================
Adversarial 3: Negative k (k=-1)
Profile: {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
----------------------------------------
Returned 29 results (k=-1)

Top Recommendations
========================================
1. Sunrise City - Neon Echo
   Score: 4.47
   Because:
     - Mood match: happy (+2.0)
     - Genre match: pop (+1.0)
     - Energy close to target 0.8 (+1.47)

2. Rooftop Lights - Indigo Parade
   Score: 3.44
   Because:
     - Mood match: happy (+2.0)
     - Energy close to target 0.8 (+1.44)

3. Pixel Crush - NOVA7
   Score: 3.38
   Because:
     - Mood match: happy (+2.0)
     - Energy close to target 0.8 (+1.38)

4. Gym Hero - Max Pulse
   Score: 2.30
   Because:
     - Genre match: pop (+1.0)
     - Energy close to target 0.8 (+1.30)

5. Groove Tunnel - Funkspot
   Score: 1.47
   Because:
     - Energy close to target 0.8 (+1.47)
```

### Adversarial 4: Acoustic bonus outweighs a genre/mood mismatch

Profile: `{"genre": "metal", "mood": "angry", "energy": 0.18, "likes_acoustic": true}`

"Morning Prelude" (classical/peaceful — a total mismatch on genre and mood) scores 2.50 and nearly ties "Static Truth" (mood-matched "angry") at 2.44, purely from stacking the energy and acoustic bonuses.

```
============================================================
Adversarial 4: Acoustic bonus outweighs genre/mood mismatch
Profile: {'genre': 'metal', 'mood': 'angry', 'energy': 0.18, 'likes_acoustic': True}
----------------------------------------
Returned 5 results (k=5)

Top Recommendations
========================================
1. Iron Curtain - Razorback
   Score: 3.31
   Because:
     - Mood match: angry (+2.0)
     - Genre match: metal (+1.0)
     - Energy close to target 0.18 (+0.31)

2. Morning Prelude - Clara Voss
   Score: 2.50
   Because:
     - Energy close to target 0.18 (+1.50)
     - Acoustic bonus (+1.0)

3. Static Truth - The Wrecks
   Score: 2.44
   Because:
     - Mood match: angry (+2.0)
     - Energy close to target 0.18 (+0.44)

4. Spacewalk Thoughts - Orbit Bloom
   Score: 2.35
   Because:
     - Energy close to target 0.18 (+1.35)
     - Acoustic bonus (+1.0)

5. Autumn Letter - Hollow Oak
   Score: 2.30
   Because:
     - Energy close to target 0.18 (+1.30)
     - Acoustic bonus (+1.0)
```

### Adversarial 5: Empty profile

Profile: `{}`

Every song scores 0.0, so ties resolve to whatever order the CSV loaded in (Python's stable sort) rather than any meaningful ranking, and the explanation string is empty.

```
============================================================
Adversarial 5: Empty profile
Profile: {}
----------------------------------------
Returned 5 results (k=5)

Top Recommendations
========================================
1. Sunrise City - Neon Echo
   Score: 0.00
   Because:
     - 

2. Midnight Coding - LoRoom
   Score: 0.00
   Because:
     - 

3. Storm Runner - Voltline
   Score: 0.00
   Because:
     - 

4. Library Rain - Paper Lanterns
   Score: 0.00
   Because:
     - 

5. Gym Hero - Max Pulse
   Score: 0.00
   Because:
     - 
```

### Adversarial 6: Case/whitespace mismatch

Profile: `{"genre": "Pop", "mood": " happy", "energy": 0.8}`

Exact string equality on `genre`/`mood` means `"Pop"` never matches `"pop"` and `" happy"` never matches `"happy"`, so every genre/mood point is silently lost and the top 5 collapses to pure energy-proximity ranking — even though a human would consider this profile a clear pop/happy match.

```
============================================================
Adversarial 6: Case/whitespace mismatch
Profile: {'genre': 'Pop', 'mood': ' happy', 'energy': 0.8}
----------------------------------------
Returned 5 results (k=5)

Top Recommendations
========================================
1. Sunrise City - Neon Echo
   Score: 1.47
   Because:
     - Energy close to target 0.8 (+1.47)

2. Groove Tunnel - Funkspot
   Score: 1.47
   Because:
     - Energy close to target 0.8 (+1.47)

3. Rooftop Lights - Indigo Parade
   Score: 1.44
   Because:
     - Energy close to target 0.8 (+1.44)

4. Fuego Libre - Los Rayos
   Score: 1.43
   Because:
     - Energy close to target 0.8 (+1.43)

5. Night Drive Loop - Neon Echo
   Score: 1.42
   Because:
     - Energy close to target 0.8 (+1.42)
```

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

I tried halving the genre weight (1.0 → 0.5) and doubling the energy weight (1.5 → 3.0). Mood stayed the strongest signal either way, but genre became almost irrelevant next to energy - songs with the right energy but wrong genre started beating songs with the right genre but slightly-off energy. It made the recommendations feel more like "energy matching" than "taste matching."

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

Only 30 songs, most genres/moods have just one song, so results repeat easily. Genre and mood have to match exactly (case and spacing matter), so close matches get zero credit. It doesn't look at lyrics, artist, or listening history, just the 4 scored numbers. Energy math breaks if the target isn't between 0 and 1. Mood counts for the most points, so it can override a better overall fit.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

Building this showed me that a recommender is really just a scoring formula someone chose weights for - there's no "understanding" of music, just numbers being compared. Small changes to those weights (like doubling energy or halving genre) noticeably changed which songs came out on top, which made me realize how much a system's "taste" depends on decisions the builder made, not the user.

Bias can sneak in through exact-match rules (typos or casing silently losing points), through which features get scored at all (valence and danceability are ignored here even though they're in the data), and through a thin catalog where niche genres/moods only have one song to ever recommend. None of that looks like "bias" in the code - it just looks like normal scoring - which is what makes it easy to miss.



