# AI Writing Patterns Reference

> Loaded exclusively by `humanizer-SKILL.md`. Do not load in other sub-skills.
> Sources: GPTZero vocabulary research, FSU/Max Planck (arxiv 2412.11385), Wikipedia Signs of AI Writing,
> Pangram Labs, Colin Gorrie rhetorical analysis, MDPI stylometric research (2025), Washington Post
> em dash analysis (2025), SCIRP hedging study (2024).

---

## Tier 1 — Always Replace

These words appear in AI-generated text at statistically anomalous rates (10x–200x human baseline).
Replace every instance unless context makes it clearly correct (see exceptions).

| AI Word/Phrase | Replace With | Exception — do NOT replace if |
|---|---|---|
| delve / delve into | examine, look at, dig into | N/A — always replace |
| leverage (verb) | use, apply, draw on | It's a financial noun ("debt leverage ratio") |
| tapestry (metaphorical) | mix, combination, blend | It literally means woven fabric |
| robust | strong, solid, reliable | Technical spec context (e.g., "robust error handling" in code docs is fine) |
| seamless / seamlessly | smooth, easy, without friction | N/A |
| transformative | significant, real, lasting, meaningful | N/A |
| pivotal | key, decisive, turning point | N/A |
| nuanced | specific, careful, layered, detailed | N/A |
| multifaceted | complex, many-sided, layered | N/A |
| comprehensive | full, thorough, complete | In academic/technical contexts where exhaustiveness is the actual claim |
| underscore (verb) | highlight, show, point to | It's used as a noun (the character `_`) |
| testament (as in "a testament to") | proof of, evidence of, sign of | N/A |
| landscape (metaphorical) | field, area, world, space, domain | Literal geographical use |
| ecosystem (metaphorical) | system, network, world | Literal biological use |
| foster | build, encourage, support, grow | N/A |
| navigate (metaphorical) | deal with, work through, handle | Literal navigation (sailing, GPS, directions) |
| holistic | whole, complete, all-round | Clinical/medical context |
| synergy | cooperation, combined effect, working together | N/A |
| cutting-edge | latest, current, leading, newest | N/A |
| innovative | new, original, fresh | N/A |
| groundbreaking | significant, notable, new | N/A |
| paradigm shift | fundamental change, new way of thinking | N/A |
| game-changer / game-changing | major shift, turning point | N/A |
| revolutionary | radical, major, new | Historical contexts (the Revolutionary War is fine) |
| empower / empowerment | help, enable, give, allow | Specific social justice/policy contexts where "empowerment" is the named concept |
| optimize | improve, fix, tune | Technical performance context (database optimization, code optimization) |
| streamline | simplify, speed up, cut steps | N/A |
| elevate | improve, raise, boost | Literal elevation (altitude) |
| harness (metaphorical) | use, capture, direct, apply | Literal (horse harness, safety harness) |
| unlock (metaphorical) | reveal, release, open up, access | Literal (unlock a door, unlock a phone) |
| unleash (metaphorical) | release, let loose, free | Literal animal contexts |
| facilitate | help, make easier, enable | Formal facilitation (e.g., "she facilitated the meeting" in a professional context) |
| elucidate | explain, clarify, show | N/A |
| illuminate (metaphorical) | explain, reveal, show | Literal light use |
| resonate | connect, appeal, ring true | Music and sound contexts |
| captivate | engage, interest, hold attention | N/A |
| embark (on a journey) | start, begin, set out | Literal sea/travel use |
| showcase | show, demonstrate, display | N/A |
| align (metaphorical) | match, fit with, support, reflect | Literal alignment (physical, typographic) |
| whilst | while | N/A — always replace |
| spearhead | lead, drive, head up | N/A |
| galvanize | motivate, push, drive | Literal (galvanized steel) |
| orchestrate | organize, manage, coordinate, arrange | Musical conducting context |
| cultivate | build, develop, grow | Literal farming/gardening |
| proliferate | spread, grow, multiply | N/A |
| eradicate | remove, end, eliminate | N/A |
| paramount | most important, top priority, critical | N/A |
| quintessential | typical, classic, defining example of | N/A |
| unparalleled | unmatched, unique, exceptional | N/A |
| invaluable | very useful, essential, critical, important | N/A |
| actionable | practical, useful, something you can act on | N/A |
| pain points | problems, issues, frustrations, challenges | N/A |
| commendable | impressive, good, well done | N/A |
| scalable | expandable, able to grow | Technical architecture context (scalable infrastructure) is fine |
| endeavour | try, attempt, work, aim | N/A |
| certainly | [delete — it adds nothing] | N/A |
| indeed | [delete — it adds nothing] | N/A |
| in order to | to | N/A |
| due to the fact that | because | N/A |
| at this point in time | now | N/A |
| for the purpose of | for, to | N/A |
| in the event that | if | N/A |

---

## Tier 2 — Usually Replace

These are AI-favored but context-dependent. Apply judgment.

| AI Word/Phrase | Replace With | When to keep |
|---|---|---|
| furthermore | also, and — or delete the connector | Genuine logical extension in formal writing |
| moreover | also — or delete | Rare formal writing with a specific additive claim |
| additionally | also, and, in addition | Formal or technical writing where additive structure is explicit |
| consequently | so, as a result | Causal logic that needs explicit marking |
| nevertheless | still, even so, but | Genuine concessive logic |
| nonetheless | still, even so | Same as nevertheless |
| thus | so, therefore | Mathematical or formal argument |
| hence | so, which means | Same as thus |
| therefore | so, which means | Same as thus |
| insights | findings, lessons, observations | When "insight" is genuinely the right word (a sudden realization) |
| journey (metaphorical) | process, experience, path, story | When the metaphor is intentional and specific |
| community | [replace with specific group name] | When referring to a real, named community |
| conversation | [use more specific verb: "debate", "discussion", "exchange"] | When "conversation" is deliberately used for its informal warmth |
| story | [use if genuinely narrative] | Literal storytelling |
| explore | look at, consider, examine | When "explore" is used with genuine openness (not as a decoration) |
| dive into | [only use if brief and intentional] | When used sparingly and the context is casual |
| unpack | examine, break down, look at | N/A |
| impactful | effective, meaningful, significant | N/A |
| utilize | use | Highly technical contexts where "utilize" means specifically "make use of in a functional capacity" |

---

## Filler Phrases — Delete Entirely

These phrases introduce claims without adding information. Delete the phrase; the claim stands alone.

- "It's worth noting that..."
- "It's important to note that..."
- "It should be noted that..."
- "It's crucial to understand that..."
- "It can be argued that..."
- "Needless to say..."
- "It goes without saying that..."
- "Generally speaking..."
- "To some extent..."
- "From a broader perspective..."
- "As we all know..."
- "Of course..."
- "Obviously..."
- "Clearly..."

**Rule:** Delete the entire phrase and start directly with the claim.
- Before: "It's worth noting that consistency matters more than frequency."
- After: "Consistency matters more than frequency."

---

## Opening Clichés — Delete and Replace

These openers appear in AI writing at 50x–107x the rate of human writing. Delete the entire opening sentence and start at the first real claim.

**Always delete:**
- "In today's fast-paced world..."
- "In today's digital landscape..."
- "In an era where..."
- "In an era of..."
- "In the ever-evolving world of..."
- "In recent years, [topic] has become increasingly..."
- "As we navigate an increasingly [adjective] world..."
- "In the age of [technology/AI/social media]..."
- "Whether you're a [beginner] or a [professional]..."
- "There's no denying that..."
- "It goes without saying that..."
- "Have you ever wondered..."

**Replacement rule:** Start with the first genuinely interesting sentence. The context sentence is almost always unnecessary — readers know what era they're in.

---

## Closing Clichés — Delete and Replace

These endings announce that the content has concluded rather than actually concluding.

**Always delete:**
- "In conclusion, ..."
- "In summary, ..."
- "To summarize, ..."
- "In essence, ..."
- "To wrap things up, ..."
- "As we move forward..."
- "By embracing [topic], we can..."
- "The future of [topic] is bright..."
- "The possibilities are endless..."
- "Together, we can [achieve something vague]..."
- "Only time will tell..."
- "This is just the beginning..."
- "Remember: [platitude]"
- A bullet-point list summarizing what was just said

**Replacement rule:** End with the most resonant, specific, forward-pointing sentence in the piece. Don't announce the ending — just end.

---

## Structural Patterns

### Em Dash Overuse
**Detection:** 2 or more em dashes in a single paragraph.
**Fix:** Replace em dashes beyond the first with: comma, colon, period + new sentence, or rewrite.
**Keep one** if it's being used correctly for a genuine dramatic pause.
- Before: "The solution — which many overlook — is surprisingly simple — and it's free."
- After: "The solution, which many overlook, is surprisingly simple. And it's free."

### Rule of Threes (Tricolon Overuse)
**Detection:** Every supporting idea in the piece comes in exactly three items.
**Fix:** Break at least one group — use two, or four, based on what the content actually needs.
- Before: "It is fast, reliable, and scalable."
- After: "It is fast and reliable." (if only two properties actually matter)

### "Not Just X, It's Y" Construction
**Detection:** Antithesis pattern — "not just/merely X, it's Y", "it's not about X, it's about Y".
**Fix:** Delete the X clause entirely. State Y directly.
- Before: "This isn't just about speed — it's about trust."
- After: "This is about trust."

### Significance Signposting
**Detection:** Phrases announcing importance rather than demonstrating it.
- "plays a crucial role in [X]"
- "underscores the importance of [X]"
- "highlights the significance of [X]"
- "reflects the continued relevance of [X]"
- "a pivotal moment in [X]"
**Fix:** Delete the phrase. State X directly.
- Before: "This moment underscores the importance of clear communication."
- After: "Clear communication determines the outcome."

### Forced Balanced Arguments (Both-Sidesing)
**Detection:** "On one hand... on the other hand..." or "While some argue X, others contend Y" when no genuine tension exists.
**Fix:** Commit to the stronger position. Delete the weaker side.
**Exception:** If genuine, specific tension exists with a named tradeoff, the balance can stay — but make each side concrete, not vague.

### Formulaic Elaboration (Triple Restatement)
**Detection:** A claim, then the same claim restated, then restated again in three consecutive sentences.
**Fix:** Delete the 2nd and 3rd restatement. The first statement is sufficient.
- Before: "Clarity matters. In other words, being clear is essential. What this means is that you should always write clearly."
- After: "Clarity matters."

### Uniform Sentence Length (Low Burstiness)
**Detection:** All sentences in a paragraph are 12–18 words. No very short, no very long.
**Fix:** Add one sentence under 7 words. Allow one to run longer without breaking it.
**Note:** GPTZero's burstiness metric is the single most reliable AI text detector — vary length deliberately.

### Passive Voice Detachment
**Detection:** "It has been shown that...", "It is believed that...", "Research has demonstrated..."
**Fix:** Name the subject. "Several studies show...", "Many engineers believe...", "MIT researchers found..."
**Exception:** Passive is fine when the agent genuinely doesn't matter or is unknown.

### Bullet Obsession
**Detection:** Every idea in the piece is expressed as a bullet list. Prose is absent.
**Fix:** Convert at least one bullet section to connected prose. Keep bullets only where items are genuinely parallel and enumerable.

---

## Tonal Markers

### False Intimacy Phrases
These perform closeness without genuine personal stake. Delete or replace with actual personal voice.
- "Here's the thing..."
- "Here's an uncomfortable truth..."
- "Let me be honest with you..."
- "The truth is..."
- "What no one tells you is..."
- "Let's be real..."
- "Let's dive in."
- "Let's explore..."
- "You might be wondering..."
- "I understand you might be thinking..."

**Fix:** Either use a genuine personal observation with actual experience behind it, or drop the framing and start the actual point.

### Excessive Positivity
AI describes everything in maximally positive terms. Never expresses doubt, frustration, or genuine criticism.
- "fascinating", "incredible", "remarkable", "captivating", "majestic", "breathtaking" — as default descriptors
- "Exciting possibilities", "Remarkable insights", "Powerful tools"
**Fix:** Use restrained language. Let the actual subject carry the weight. One well-placed strong adjective beats five weak enthusiasms.

### Corporate Inspirational Tone
- "Unlock your potential..."
- "Push the boundaries of..."
- "At the forefront of..."
- "Pave the way for..."
- "Bridging the gap between..."
- "Transforming the way we..."
- "Shaping the future of..."
- "Empowering individuals to..."
- "Creating a world where..."
**Fix:** Specific, grounded language with concrete nouns and measurable verbs.

---

## Platform-Specific Rules

### Twitter/X
- No em dashes
- No "furthermore", "moreover", "additionally"
- Contractions required (don't, can't, I'm, it's)
- No conclusion tweet ("So that's X in a nutshell...")
- No opener tweet that contextualizes the era

### LinkedIn
- "Journey", "community", "together", "story" banned unless used very specifically
- No inspirational closer
- No "just wanted to share"
- No "honored and humbled"
- Specificity beats vague warmth in every case

### Newsletter
- Don't over-clean — some informality is correct here
- One personal aside is expected and fine
- Vary sentence rhythm; long-form allows complexity
- Don't remove first-person observations

### TikTok / YouTube Shorts script
- Sentence fragments permitted
- Slang permitted
- Match spoken rhythm, not written grammar
- Passive voice almost never appropriate

### Instagram Carousel
- Each slide: one declarative sentence preferred
- No connectors between slides
- Each slide should stand alone as a unit

### Bluesky / Threads
- Like Twitter but slightly more discursive
- No "moreover"
- Conversational — intellectual is fine but academic is not

### Podcast Talking Points
- Conversational fragments OK
- Write how people actually speak
- No bullet lists as final output (they become notes, not deliverables)

---

## Substitution Quick Reference

| AI Default | Human Alternative |
|---|---|
| delve into | look at, examine, explore |
| leverage | use, draw on, apply |
| utilize | use |
| robust | strong, solid, reliable |
| seamless | smooth, easy |
| transformative | significant, real, lasting |
| comprehensive | full, thorough, complete |
| pivotal | key, decisive, turning |
| crucial role | important part |
| testament to | proof of, evidence of |
| landscape | field, area, space |
| foster | build, encourage, support |
| navigate challenges | deal with, work through |
| cutting-edge | latest, current, new |
| innovative | new, original |
| groundbreaking | significant, notable |
| paradigm shift | fundamental change |
| game-changer | major shift |
| empower | help, enable, give |
| optimize | improve, fix |
| streamline | simplify, speed up |
| elevate | improve, raise |
| harness | use, capture |
| unlock potential | reveal, release |
| facilitate | help, make easier |
| it's worth noting | [just state the point] |
| it's important to note | [just state the point] |
| In today's fast-paced world | [delete the opener] |
| In conclusion | [delete; just conclude] |
| furthermore | also, and — or omit |
| moreover | also — or omit |
| In order to | To |
| due to the fact that | because |
| at this point in time | now |
| in the event that | if |
| for the purpose of | for, to |
| showcase | show, demonstrate |
| align with | match, fit with, support |
| articulate | say, express, explain |
| resonate | connect, appeal, ring true |
| embark on | start, begin |
| cultivate | build, develop, grow |
| eradicate | remove, end, eliminate |
| paramount | most important, top priority |
| invaluable | very useful, essential |
| actionable | practical, useful |
