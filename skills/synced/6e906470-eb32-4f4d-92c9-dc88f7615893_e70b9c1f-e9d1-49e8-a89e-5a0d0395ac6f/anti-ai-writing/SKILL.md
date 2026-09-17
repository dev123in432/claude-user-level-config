---
name: anti-ai-writing
description: >
  Audit and rewrite content to remove AI writing patterns, or write new content that reads as human from the start.
  Use this skill whenever the user asks to "clean up" writing, "remove AI tells", "make this sound human",
  "humanise this", "audit for AI patterns", "de-slop", "write like a human", or any variation.
  Also trigger when the user asks to write new content and mentions wanting it to sound natural, authentic,
  not AI-generated, or human. Trigger on phrases like "write this properly", "no AI voice",
  "make it sound like me", "anti-AI", "anti-slop", or "humanise". Use for blog posts, proposals,
  LinkedIn posts, emails, reports, SOWs, case studies, landing pages, and any prose output.
  If in doubt about whether to use this skill, use it - false positives are better than letting AI slop through.
---

# Anti-AI Writing Engine

Transform any content into authentic, human-sounding prose by eliminating AI patterns and applying proven writing fundamentals.

**Core philosophy:** The best writing is invisible. Readers should feel like they're reading a real person's thoughts - not processed, filtered, or generated content.

## When to Use This Skill

- Reviewing and humanising AI-generated drafts
- Writing content that must not appear AI-assisted
- Editing any prose for authenticity and impact
- Quality-checking content before publication

Pairs well with voice style modules for writing in a specific author's tone.

## Two Modes of Operation

### Mode 1: Audit & Rewrite

When the user provides text to clean up, return four sections:

**Section 1 - Issues Found**
List every AI pattern detected. Quote the offending text. Name the pattern category.

**Section 2 - Rewritten Version**
The full clean text. No commentary mixed in. Just the clean output.

**Section 3 - What Changed**
Brief summary of the major edits and why they matter.

**Section 4 - Second Pass Audit**
Re-read the rewrite. AI patterns survive the first edit more often than you'd expect. Catch anything that slipped through - recycled transitions, lingering inflation, copula swaps, uniformity. If you find issues, fix them and note what you caught.

### Mode 2: Write Clean

When drafting new content, internalise every rule below before writing a single word. Do not write a draft and then clean it up. Write it right the first time.

After finishing the draft, do a silent self-audit against all patterns below. Fix anything you catch. Do not mention this self-audit to the user unless they ask.

---

## Universal Writing Fundamentals

Master these principles first, then layer on specific style choices.

### 1. Energy Transfer

The best writing is a transfer of energy from writer to reader.

Write conversations, not speeches. Speak WITH your audience, not AT them. Remove corporate jargon, academic language, and buzzwords.

❌ "The implementation of our innovative frameworks has demonstrated significant positive outcomes in terms of engagement metrics."
✅ "Our new approach works. People are paying attention."

The second version transfers energy. Readers feel conviction, not formality. Every word must earn its place.

### 2. Conciseness is King

Process: Write your first draft freely. Read it aloud. Delete anything that repeats an idea already stated, softens your main point, sounds formal instead of conversational, or takes more words than necessary.

❌ "Our approach incorporates multiple methodologies designed to accommodate diverse requirements and development patterns."
✅ "We adapt to how you work."

### 3. The SUCKS Framework

Before writing anything, answer these questions:

**S - Specific.** Write for ONE person, not a crowd. Know their struggles, goals, language. If you write for everyone, you write for no one.

**U - Unique & Useful.** Does this change how your reader thinks, feels, or acts? Unique means they haven't seen this perspective before. Useful means they can actually apply this.

**C - Clear, Curious, Conversational.** Main idea is unmissable. Questions make readers think. It reads like talking to a friend.

**K - Kept Simple & Structured.** Simple ideas, simple words. Clear beginning, middle, end.

**S - Sticky.** Memorable phrases they'll repeat. Ideas that lodge in memory.

Application checklist before writing:
- Who is my ONE reader?
- What will they think, feel, or do differently?
- Could a 12-year-old understand the main point?
- Does this flow like a conversation?

### 4. Be Undeniable

Transform vague claims into concrete specifics.

❌ "How to boost your results by at least 87% in just one month."
✅ "This year, I helped 13 clients boost their results by 87%-256% in just one month. Here's how:"

Pattern: Replace vague language with data, examples, specifics, or personal experience.

### 5. Craft Sticky Sentences

Use these techniques to create memorable statements:

**Alliteration** - Same starting sounds: "Specificity is the secret"

**Symmetry** - Parallel structure: "Read for awareness. Write for understanding."

**Contrast** - Opposing ideas: "To be everywhere is to be nowhere."

**Rhyme** - Similar ending sounds: "Tell a story or lose your glory"

**Rhythm** - Pleasing cadence: "When you can't wait to share it, they can't help but read it"

For maximum stickiness, combine techniques: "Anger prepares us to fight. Fear prepares us to flee." (Symmetry + Alliteration)

See references/sticky-sentences.md for expanded examples.

---

## Forbidden Patterns (AI Tells)

These patterns consistently signal AI involvement. Eliminate them aggressively.

### The Correlative Construction (Most Common AI Tell)

This is the #1 pattern to avoid:

❌ "X aren't just Y - they're Z"
❌ "X isn't just about Y, it's about Z"
❌ "Teachers aren't just instructors - they're mentors"

Why it's bad: This is the default structure AI models produce. Every AI writing sample uses this.

Better alternatives:
✅ "Teachers mentor students"
✅ "X accomplishes both Y and Z"
✅ State the point directly

### Forbidden Constructions

❌ "It's not about X, it's about Y"
❌ "The truth is..." / "The reality is..."
❌ "Let that sink in"
❌ "Now more than ever..."

Better: State your point directly without setup.

### Forbidden Rhetorical Flourishes

❌ "The best part? ..."
❌ "The secret? ..."
❌ "Sounds impossible? It's not."
❌ "What if I told you..."
❌ "Here's the thing..."
❌ "Let's be honest..."
❌ "At the end of the day..."

### Forbidden Staccato Phrasing

Do not use faux-dramatic sentence fragments:

❌ "No fluff. No filler. Just results."
❌ "Big ideas. Small words. Maximum impact."
❌ "Simple. Clear. Effective."
❌ "Stop guessing. Start winning."

### Forbidden Openers

❌ "In the ever-evolving world of..."
❌ "In today's fast-paced..."
❌ "Gone are the days when..."
❌ "This underscores..."
❌ "In an era where..."

### Formatting Restrictions

- Do not use boldface for emphasis in body text
- Do not use emojis unless explicitly requested
- Do not add summaries like "In conclusion" or "In summary"
- Do not rely on bullet points unless explicitly asked

### Dash Usage

Use regular hyphens with spaces for parenthetical breaks - like this - not em dashes (—) or en dashes (–).

✅ "Education is changing - and parents are noticing"
❌ "Education is changing—and parents are noticing"

---

## Anti-AI Pattern Detection

Beyond forbidden syntax, these patterns consistently signal AI involvement:

### 1. Overuse of "Just"

AI uses "just" constantly as a softener.

❌ "We just need to understand that it's just about learning, and we just have to focus on what matters."
✅ "It's about learning. Focus on what matters."

When "just" is acceptable: "just one question," "just in case," "just started"

When to remove it: Middle of sentences as a softener, more than once per paragraph

### 2. Overuse of "Actually"

AI uses "actually" to sound like it's adding nuance.

❌ "It's actually about teaching, but actually about community, and students actually need both."
✅ "It's about teaching. It's also about community. Students need both."

When acceptable: Correcting a previous misunderstanding. Limit to once per 500 words maximum.

### 3. Hedging Language

AI loves hedge words because they make uncertain claims safer. But they make writing weak.

❌ "This might help you" → ✅ "This will help you"
❌ "Some people say..." → ✅ "I've found that..."
❌ "It could be argued that..." → ✅ "It's true that..."
❌ "Perhaps we should consider..." → ✅ "We should..."
❌ "One could say..." → ✅ "This is true because..."

Test: If you find "might," "could," "perhaps," "possibly," "maybe," "somewhat," or "it seems like," ask: Do I actually believe this? If yes, remove the hedge.

### 4. Passive Voice

AI defaults to passive voice because it's safer.

❌ "It was determined that improvements were needed"
✅ "We need to improve"

❌ "It has been shown that users benefit from..."
✅ "Users benefit from..."

Test: If you can't identify who's doing the action, it's passive. Rewrite with a subject.

### 5. Corporate Jargon

❌ "Leveraging synergies across stakeholder ecosystems"
✅ "Getting different people talking to each other"

❌ "Optimise engagement metrics"
✅ "Get people paying attention"

Test: Would you say this to a friend? If not, rewrite it plainly.

### 6. Vague Language

AI tends toward vagueness because it's safer. Vague writing is weak writing.

❌ "Our users improve" → ✅ "Users improve by 40% in 6 months"
❌ "Many people think..." → ✅ "A survey found that 73% of users..."
❌ "Significant improvements" → ✅ "Improvements of 23-47%"

Test: Can you back it up with a specific number, example, or name?

### 7. Too Many Transition Words

AI overuses transitions trying to seem sophisticated.

❌ "Furthermore, it is important to note that, in addition to this, moreover..."
✅ Strong structure needs fewer transitions

Limit transitions to: but, and, so, then, because

### 8. Overcomplicated Sentence Structure

❌ "The multifaceted nature of contemporary paradigms, which encompasses diverse modalities and approaches, necessitates a comprehensive reevaluation of traditional methodologies."
✅ "Things have changed. We need to rethink our approach."

---

## The Humanisation Workflow

### Step 1: Understand Your Source

What's the core insight or story? What's the emotional arc? What's the most important takeaway?

Ask yourself: What's being said that no one else is saying? What will readers think, feel, or do differently? What's the 30-second version?

### Step 2: Apply the SUCKS Framework

Run through the checklist: Who is my ONE reader? Is this unique and useful to them? Can I make it clear, curious, and conversational? How do I keep it simple and structured? What will stick with them?

### Step 3: Write or Edit the Draft

If writing fresh: Write freely without self-editing. Get the ideas down first. Polish in subsequent passes.

If editing AI output: Read the entire draft. Identify the core message. Rewrite rather than patch.

### Step 4: Apply Sticky Sentences

Identify 2-3 most important statements and strengthen them. Add alliteration, symmetry, contrast, or rhythm. Make them quotable. Make them memorable.

### Step 5: Eliminate AI Tells (Critical)

Go through systematically and remove:
- Correlative constructions ("X aren't just Y, they're Z")
- Overuse of "just" and "actually"
- Hedge words (might, could, perhaps, seems)
- Passive voice
- Corporate jargon
- Vague language (replace with specifics)
- Forbidden patterns ("Let that sink in," etc.)
- Too many transitions
- Overcomplicated sentences

Test for each sentence: Would this sentence appear in a ChatGPT output? If yes, rewrite it.

### Step 6: Read Aloud & Quality Check

Read your entire piece aloud:
- Does it sound like a real person talking?
- Does energy transfer (not feel formal)?
- Is every sentence earning its place?
- Do important ideas have sticky phrasing?
- Are there obvious AI tells remaining?

If you answer "no" to any question, fix it before publishing.

---

## Quick Reference Checklists

### The "Would a Human Write This?" Test

For each paragraph, ask:
1. Does it sound like how I actually talk?
2. Is there unnecessary formality?
3. Are there words I'd never use in conversation?
4. Does it take the long way to make a point?
5. Does it hedge when I'm actually certain?

### The AI Tell Scan

Before publishing, scan for:
- "It's not X, it's Y" constructions
- "Just" appearing more than once
- "Actually" as sentence filler
- Passive voice ("was determined," "has been shown")
- Hedge words ("might," "could," "perhaps")
- Corporate speak ("leverage," "optimise," "ecosystem")
- Vague claims without specifics
- Overused transitions ("furthermore," "moreover")
- Complex sentences that could be simple
- Rhetorical flourishes ("The best part?")
- Em dashes or en dashes (use hyphens with spaces)
- Forbidden staccato phrasing ("No fluff. No filler.")
- Forbidden openers ("In today's fast-paced...")
- Boldface used for emphasis in body text

### Elements of Effective Content

Include in your writing:
- Immediate attention - First sentence hooks
- Specific numbers - "1.5 million" not "many"
- Pattern interrupts - Surprise the reader
- Direct problem-addressing - Name the struggle
- Confidence - Eliminate hedge words
- Concrete benefits - "Double output in 30 days" not "boost productivity"
- Powerful questions - Make readers think
- Warnings/stakes - Create urgency

---

## Writing for Accelerate Tech

When the context is Accelerate Tech content (proposals, SOWs, case studies, website copy, LinkedIn), also apply:

- Direct, conversational tone. Talk to the reader like a smart colleague.
- No management consulting jargon unless the client uses it first.
- Concrete outcomes over abstract capabilities. "We reduced their deployment time from 3 days to 4 hours" beats "We streamlined their deployment pipeline."
- Australian English spelling throughout (colour, organisation, behaviour, analyse).
- No em dashes anywhere. Hard rule for all Accelerate content.
- Sentence case for all headings.

---

## Reference Files

Read these references before doing any audit work. They contain the detail that makes the difference between catching surface-level tells and catching everything.

- `references/vocabulary.md` - Full tiered word replacement table (109 entries across 3 tiers)
- `references/patterns.md` - Complete pattern detection categories with before/after examples (36 categories, 6 groups)
- `references/sticky-sentences.md` - Extended guide to memorable phrasing techniques
