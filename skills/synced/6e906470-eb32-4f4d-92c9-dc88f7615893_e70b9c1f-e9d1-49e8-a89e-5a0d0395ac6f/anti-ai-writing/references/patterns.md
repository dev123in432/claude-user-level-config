# AI Writing Pattern Categories

36 pattern categories organised into six groups. Each has a description, why it matters, and before/after examples.

---

## Group 1: Content Patterns

### 1. Significance Inflation
AI inflates the importance of everything. A new hire becomes "a pivotal addition". A software update becomes "a watershed moment".

Before: "This partnership marks a watershed moment in the evolution of cloud computing."
After: "The partnership gives us access to Azure's Sydney data centre."

### 2. Notability Name-Dropping
AI stacks famous names for credibility without connecting them to specific claims.

Before: "Featured in The New York Times, Wired, and TechCrunch, the platform has gained significant attention."
After: "In a March 2024 Wired review, the platform scored 4.5/5 for query speed."

### 3. Superficial -ing Analysis
AI tacks present participle phrases onto sentences to add fake depth: "symbolising... reflecting... showcasing... highlighting..."

Before: "The design reflects the community's deep connection to the land, symbolising growth and highlighting local heritage."
After: "The architect chose native sandstone because it's cheaper and weathers well in coastal conditions."

### 4. Promotional Language
AI defaults to travel-brochure language. Everything is vibrant, stunning, nestled, or breathtaking.

Before: "Nestled within the breathtaking landscape of the Northern Tablelands, this vibrant community thrives."
After: "Armidale is a university town in northern NSW with a population of about 25,000."

### 5. Vague Attribution
AI cites "experts" and "studies" without naming them.

Before: "Studies show that organisations using AI see a 40% improvement in productivity."
After: "McKinsey's 2024 survey of 600 companies found that AI adopters reported 15-25% time savings on repetitive tasks."

If you can't name the source, cut the claim.

### 6. Formulaic Challenges
AI uses "Despite challenges... continues to thrive" as a transition crutch.

Before: "Despite challenges in the competitive landscape, the company continues to thrive."
After: "They lost two enterprise clients to Datadog in Q3 but signed four new ones in healthcare."

### 7. False Ranges
AI implies breadth by listing unrelated things in a range.

Before: "From quantum computing to social media, technology continues to reshape every aspect of our lives."
After: Name the actual topics being discussed.

---

## Group 2: Language Patterns

### 8. Banned Word Usage
See references/vocabulary.md for the full tiered replacement table.

### 9. Copula Avoidance
AI avoids "is" and "has" in favour of fancier constructions: "serves as", "functions as", "stands as", "boasts", "features".

Before: "The platform serves as a unified hub for engineering teams, featuring real-time dashboards and boasting sub-second query performance."
After: "The platform is a monitoring tool with real-time dashboards and fast queries."

### 10. Synonym Cycling
AI rotates through synonyms to avoid repeating words. Humans just repeat the clear word.

Before: "Developers, engineers, practitioners, and builders across the industry..."
After: "Developers across the industry..."

### 11. Template Phrases
AI fills in mad-libs patterns: "a [adj] [noun] towards [adj] [noun]".

Before: "A significant milestone towards scalable, resilient infrastructure."
After: "They can now handle 10x the traffic without adding servers."

### 12. Filler Phrases
Phrases that add zero information.

| Remove | Replace With |
|---|---|
| In order to | To |
| Due to the fact that | Because |
| At the end of the day | (remove or use "ultimately") |
| It's worth noting that | (remove - just state the point) |
| It should be noted that | (remove) |
| In terms of | For, about |
| With respect to | About, for |
| For all intents and purposes | (remove) |
| At this point in time | Now |
| In the event that | If |
| On a [daily/weekly] basis | [Daily/weekly] |

### 13. Sticky Sentences
Sentences where over 45% of words are "glue words" (articles, prepositions, pronouns, conjunctions) that carry no meaning.

Before: "It is important to note that there are a number of factors that need to be taken into consideration at this time."
After: "Three factors matter here."

### 14. Adverb Overuse
AI uses adverbs as crutches: "significantly", "substantially", "fundamentally", "remarkably".

Rule: If the adverb doesn't change the meaning when removed, remove it. "Significantly improved" is usually just "improved".

---

## Group 3: Structure Patterns

### 15. Formatting Tells
- Em dashes (—) and en dashes (–): Replace with hyphens-with-spaces or restructure
- Bold overuse: Reserve for actual emphasis, not every key phrase
- Emoji in headers: Remove unless user requests them
- Bullet-heavy structure: Convert to prose when the content is narrative
- Excessive headers: Not every paragraph needs a heading

### 16. Sentence Structure Uniformity
AI writes sentences of similar length. Human writing alternates between short punches and longer explanations.

Check: If five consecutive sentences are within 3 words of the same length, rewrite for variety.

### 17. Paragraph Uniformity
AI makes every paragraph the same length (usually 3-4 sentences). Humans write paragraphs that range from one sentence to eight.

### 18. Transition Phrase Overuse
AI connects every paragraph with a transition: "Moreover," "Furthermore," "Additionally," "In addition," "However,"

Rule: If you can remove the transition word and the paragraph still makes sense, remove it. Use "and", "but", "also" if you need a connector. Or just start the new thought.

### 19. Inline-Header Lists
AI formats lists as "**Category:** Description of the category..."

Before: "**Speed:** The platform delivers sub-second queries. **Scale:** It handles millions of events."
After: "Queries return in under a second. The platform handles millions of events per day."

### 20. Title Case Headings
AI capitalises every word in headings.

Before: "Strategic Negotiations And Partnerships For Growth"
After: "Strategic negotiations and partnerships for growth"

### 21. Three-Item Lists
AI defaults to listing three things in every sentence and every section. Two items is more natural. Four is fine for actual lists.

Before: "The platform is fast, reliable, and scalable."
After: "The platform is fast and reliable." (If scalability matters, give it its own sentence with specifics.)

---

## Group 4: Communication Patterns

### 22. Chatbot Openers
Remove entirely: "Certainly!", "Absolutely!", "Great question!", "Of course!", "That's a fantastic point!"

### 23. Chatbot Closers
Remove entirely: "I hope this helps!", "Let me know if you need anything else!", "Feel free to reach out!", "Happy to help!"

### 24. Cutoff Disclaimers
Remove: "While details are limited based on available information...", "Based on my training data...", "It could potentially be argued..."

### 25. Hedge Stacking
One hedge per paragraph maximum.

Before: "It could potentially be argued that there might be some possible benefits to this approach."
After: "This approach has benefits." (Then list them specifically.)

### 26. False Emotion
AI performs emotions it doesn't have.

Before: "What fascinated me most about this research was the truly remarkable finding that..."
After: State the finding. The reader will decide if it's remarkable.

### 27. Generic Conclusions
AI wraps everything in a bow.

Remove: "The future looks bright", "Only time will tell", "One thing is clear...", "In conclusion...", "As we move forward..."

Better: End with a specific observation, a question worth asking, or a concrete next step. Or just stop writing when you've made your point.

---

## Group 5: Rhythm and Voice Patterns

### 28. Metronomic Rhythm
AI writes with consistent sentence length and cadence. Human writing has bursts - short punches followed by longer explanations.

Fix: After writing, read it aloud. If it sounds like a metronome, break up the rhythm. Throw in a two-word sentence. Then follow with something longer.

### 29. Passive Voice Default
AI defaults to passive constructions.

Before: "The update was deployed by the team after testing was completed."
After: "The team deployed the update after testing."

### 30. No Opinions
AI presents everything as neutral. Humans have opinions and aren't afraid to share them.

Before: "There are various approaches to this problem, each with their own advantages and disadvantages."
After: "The best approach is X, because Y. The alternative costs twice as much and takes three times as long."

### 31. Over-Politeness
AI is relentlessly agreeable and polite. Human writing has personality and directness.

Before: "That's a wonderful question! There are indeed some really interesting considerations here."
After: "Here's what matters."

### 32. Abstraction Over Specifics
AI defaults to abstract language. Good writing is specific.

Before: "Our approach incorporates multiple methodologies designed to accommodate diverse requirements."
After: "We use three methods: X for speed, Y for accuracy, Z for compliance."

---

## Group 6: Document-Level Patterns

### 33. Predictable Structure
AI documents follow the same structure every time: introduction, overview, detailed sections, conclusion. Mix it up. Lead with the conclusion. Start with an example. Open with a number.

### 34. Mirror Structure
Every section follows the same internal pattern (problem-solution-benefit, problem-solution-benefit). Vary the internal structure.

### 35. Throat-Clearing Introductions
AI writes long introductions before getting to the point.

Before: "In today's rapidly evolving digital landscape, organisations face unprecedented challenges in managing their technology infrastructure. As we navigate these complex waters, it becomes increasingly important to consider..."
After: Start with the point. "Accelerate Tech builds AI solutions for government and enterprise clients."

### 36. Kitchen-Sink Paragraphs
AI tries to address everything in every paragraph. Good writing makes one point per paragraph and moves on.

---

## The Quick Audit Checklist

Run this after any edit or new draft:

1. Any Tier 1 banned words remaining? Replace them.
2. Any em dashes? Replace with hyphens or restructure.
3. Are five consecutive sentences within 3 words of the same length? Vary the rhythm.
4. Any "serves as" / "boasts" / "features"? Replace with "is" / "has".
5. Any "Moreover" / "Furthermore" / "Additionally" opening a paragraph? Remove or replace.
6. Any vague "experts say" / "studies show"? Name the source or cut the claim.
7. Any chatbot opener or closer? Remove entirely.
8. Could you cut 20% of the words? Do it.
9. Read it aloud. Does it sound like a person talking? If not, rewrite the flat parts.
10. Does it end with a generic conclusion? Cut it or replace with something specific.
