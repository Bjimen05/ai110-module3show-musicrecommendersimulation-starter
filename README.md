# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

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
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



