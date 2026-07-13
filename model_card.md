# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

MusicMatch

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

MusicMatch takes a short taste profile (favorite genre, favorite mood, target energy, and whether you like acoustic songs) and returns the top-k closest matching songs from a small catalog, with a plain-language explanation for each pick. It assumes the user can name their preferences upfront in exact terms - it doesn't learn from listening history or feedback. This is a classroom project for practicing scoring/ranking logic, not a production recommender.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Every song has a genre, a mood, an energy level, and how acoustic it sounds. You tell it your favorite genre, favorite mood, target energy, and whether you like acoustic songs. Each song earns points for matching: +2 for matching mood, +1 for matching genre, up to +1.5 for having energy close to what you asked for, and +1 more if you like acoustic and the song is acoustic. Add up the points, sort every song highest to lowest, and hand back the top few. I kept the starter's basic idea but wrote the actual point values and the energy-closeness math myself, since the starter left those as blanks.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The catalog has 30 songs covering 27 different genres and 19 different moods, so most genres and moods only have one song representing them. I used the starter CSV as-is without adding or removing songs. Since almost every genre/mood is a singleton, the dataset doesn't really capture variety within a taste - there's no way to compare two different "happy pop" songs against each other since there's usually only one.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

It works best for users who type common genres/moods that appear more than once in the catalog (like "happy," "chill," or "intense"), since there's actually more than one song to rank against each other. The mood + genre + energy combo correctly picks out the one song that's a true triple match as the #1 result every time, which matches my intuition - e.g. asking for pop/happy/high energy correctly surfaces an upbeat pop song first.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

One weakness I found is there were no artist variety, which mean the system don't prevent recommending multiple songs by the same artist, as well as acoustic bonus is one-way, so users who like acoustic songs get a bonus but those who don't arent't penalized, so acoustic songs still appear.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested the 3 built-in profiles (pop/happy/0.8, lofi/chill/0.3 + likes acoustic, metal/angry/0.95) plus a handful of "weird" profiles to see if I could break it: an energy target way outside 0-1 (5.0), a non-numeric energy ("high"), a negative k, an empty profile {}, and a genre/mood typed with different casing and spacing ("Pop", " happy").

What surprised me most was how brittle the exact-match string comparisons are. Typing "Pop" instead of "pop" loses the genre point completely, and a stray leading space on "happy" loses the mood point too - both drop out of an otherwise perfect match and the score falls from 4.47 to 1.47. I expected the system to be forgiving of that kind of thing, but it isn't.

I also didn't expect the energy formula to have no floor. Setting energy to 5.0 instead of a normal 0-1 value made a song that matched mood AND genre score -1.54, worse than songs with no match at all. Same with a negative k - I assumed k=-1 would return nothing, but it actually returned 29 of 30 songs, because of how Python slicing handles negative numbers.

Comparing pairs of profiles:

- **pop/happy/0.8 vs lofi/chill/0.3+acoustic**: the lofi profile's top pick scores higher overall because it also gets the acoustic bonus on top of mood+genre+energy, which the pop profile never triggers since it doesn't set likes_acoustic. Makes sense - it's just one more bonus available to one profile and not the other.
- **lofi/chill/0.3 vs metal/angry/0.95**: totally different top 5s with zero overlap. Makes sense since the energy target alone (0.3 vs 0.95) pushes them to opposite ends of the catalog before mood/genre even matter.
- **pop/happy/0.8 vs metal/angry/0.95**: both land a "perfect" top pick around the same score (~4.47), which makes sense - each profile has one song in the catalog that matches mood, genre, and energy all at once, and the recipe treats every mood/genre label the same way, so an equally strong match scores the same regardless of which genre it is.
- **pop/happy/0.8 vs the same profile with "Pop"/" happy"**: identical profile to a human, but score drops from 4.47 to 1.47 because == is case- and whitespace-sensitive. This is the clearest sign the system needs to normalize strings before comparing them.
- **metal/angry/0.95 vs metal/angry/energy=5.0**: same genre and mood, but the out-of-range energy turns a +4.47 into a -1.54 for the exact same song. Shows the energy formula only works if target_energy is already between 0 and 1 - nothing stops you from putting in something outside that range.
- **metal/angry/0.95 vs metal/angry/0.18+likes_acoustic**: lowering the energy target and adding the acoustic preference doesn't change who's #1 (Iron Curtain still wins), but it drops its score enough that a completely unrelated song (Morning Prelude, classical/peaceful) climbs to a near-tie right behind it, just from stacking the energy and acoustic bonuses. Shows those bonuses can add up to about as much as a real mood match.
- **pop/happy/0.8 vs an empty profile {}**: the real profile gives a clearly ranked list; the empty profile gives every song a score of 0.0, so the "top 5" is really just whatever order the songs happen to be in the CSV. Makes sense since no scoring rule can fire with nothing to compare against, but it means an empty profile fails silently instead of saying "I have nothing to go on."

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

Next I'd add valence and danceability into the score since they're already in the data but unused, normalize genre/mood strings (lowercase + trim) so typos and casing don't lose points, clamp energy so out-of-range inputs can't produce negative scores, and add an artist-diversity rule so the top-k doesn't repeat the same artist. I'd also let users list a few genres/moods instead of just one, to better match real, mixed tastes.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Building this showed me how much a recommender's "personality" comes down to a handful of arbitrary weight choices, small tweaks like doubling energy or halving genre completely changed which songs felt right. I was surprised how easily exact-match rules break on things a human would consider identical, like "Pop" vs "pop." It made me a lot more skeptical of real recommendation apps, a lot of what feels like the app "getting me" is probably just a few hardcoded weights working out in my favor for that one search.
