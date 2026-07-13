# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

I asked it to add 5+ new, more complex song attributes (popularity, release decade, secondary mood tags, language, explicit flag) that weren't in the starter dataset, and update both the CSV and the scoring logic to actually use them.

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

"introduce 5 or more complex attributes to my dataset that are not present in the baseline data, like song popularity (0-100), Release Decade or deatailed mood tags ("nostalgic", "aggressive"), update both data/songs.csv and scoring logic src/recommender.py so scoring accounts for new attributes"

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

It rewrote `data/songs.csv` with 5 new columns (popularity, release_decade, secondary_moods, language, explicit) filled in for all 30 songs, then updated `src/recommender.py`: added the new fields to the `Song`/`UserProfile` dataclasses with safe defaults, added `BOOL_FIELDS` parsing to `load_songs`, and added 5 new scoring rules to `score_song` (secondary mood match, decade match, language match, a scaled popularity bonus, and an explicit-content penalty). It ran `pytest` and a manual script afterward to confirm nothing broke.

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

I checked that the original 3 baseline profiles still scored exactly the same as before the change, that the existing tests still passed, and manually ran a profile using all 5 new preferences to confirm each bonus/penalty applied only when it should (e.g. the K-pop song correctly skipped the English-language bonus).

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

Strategy pattern.

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

I asked for two or more switchable ranking modes (Genre-First, Mood-First, Energy-Focused) and asked the agent to brainstorm a pattern that would keep the code modular. It suggested Strategy instead of writing a separate scoring function per mode, and designed it so every mode shares one scoring method and only swaps out a dictionary of weights, so adding a new mode later doesn't touch the shared logic.

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->

`ScoringStrategy` in `src/recommender.py` holds the shared scoring rules and reads point values from `self.weights`. `BalancedStrategy`, `GenreFirstStrategy`, `MoodFirstStrategy`, and `EnergyFocusedStrategy` each just override that weights dict. `recommend_songs()` accepts a `strategy` argument, and `main.py` picks one by name from the command line (e.g. `python -m src.main mood-first`).
