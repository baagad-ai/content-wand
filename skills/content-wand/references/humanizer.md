# Edit pass: specificity and fidelity

Runs in Step 6, after drafting and before `output save`. The goal is writing a reader would not skim past, not text that gets past a detector.

## What this pass is and is not

- It is: cutting filler, replacing vague claims with the source's specifics, restoring natural rhythm, and applying the Writing Style.
- It is not detector evasion. Do not describe it that way to the user and do not offer to defeat AI detectors. Detector results are unreliable, they flag human writing, and tools built to evade them tend to damage meaning. If asked, say what the pass does and offer to improve specificity further.
- Fidelity first. Every number, name, quote and link must survive. If a replacement would change a fact or remove a key claim, skip that replacement.
- Never make the piece longer. Never add new information.

The deterministic part is `cw.py lint-ai`, which counts the patterns in `ai-patterns.md` and reports each hit with its line. The judgment part is yours: read each hit in context. A word used correctly stays.

## Pass 1. Lexical

Scan for the Tier 1 and Tier 2 words and phrases in `ai-patterns.md`.

- Filler phrases ("it's worth noting", "it's important to note") are deleted whole. The point stands alone.
- Academic connectors ("furthermore", "moreover", "additionally") become "also", or go and let the link be implied.
- Opening clichés ("In today's fast-paced world", "In an era where") are deleted. Start at the first real sentence.
- Closing clichés ("In conclusion", "In summary") are deleted.
- "Leverage", "delve", "tapestry" and similar are replaced with plain words only when they are used in the flagged way. "Leverage" as a finance noun is fine.
- Never add words that were not there.

## Pass 2. Structure

- **Em dashes**: more than one per paragraph, keep the one that does real work and use a comma, colon or full stop for the rest.
- **Uniform sentence length**: if a paragraph sits at 12 to 18 words a sentence, add one short sentence (under 7 words) and let one run longer.
- **Rule of three**: if every list in the piece has exactly three items, use two or four where the content says so.
- **"Not just X, it's Y"**: delete the X clause and state Y.
- **Significance signposts** ("plays a crucial role in", "underscores the importance of"): delete, state the claim.
- **Forced balance** ("on one hand... on the other"): if there is no real tension, commit to the stronger side. If there is, make each side concrete.
- **Repeated elaboration**: claim, restate, restate again. Keep the claim.
- **Detached passive** ("it has been shown that"): name who showed it, or make it active.
- **Bullet obsession**: if every idea is a bullet, turn at least one section into prose.

## Pass 3. Specificity

This is the pass that matters most for platforms that suppress generic posts.

- Find every general statement. Replace it with the source's specific version, or delete it.
- If a paragraph has no number, name, example or concrete image, it is a candidate for cutting.
- Check the opening line against the source. Is it the most specific thing you could say?

## Pass 4. Voice

Only if a Writing Style is loaded.

1. Sentence style: if `short-punchy`, check pass 2 did not merge short sentences. If `long-flowing`, do not chop.
2. Opening patterns: if the opener does not match and meaning allows, adjust.
3. Taboo patterns: remove any.
4. Structural patterns: "no headers", "short paragraphs" and the like.
5. Vocabulary: `everyday` replaces elevated words that survived. `technical` keeps domain terms that look like AI markers but are correct.
6. `emoji_policy`, `hashtag_policy`, `signature_phrases` and `cta_style` if set.
7. The platform note in `platform_variants`, last.

Voice match is advisory. Do not tell the user the result "sounds exactly like you".

## Platform adjustments (after the passes)

| Platform | Rules |
|---|---|
| X | Contractions. No "furthermore". No recap post. No scene-setting first post. |
| LinkedIn | No "excited to share", "humbled", "journey" without a concrete referent. No inspirational closer. Specific warmth beats generic warmth. |
| Newsletter | Do not over-clean. Keep one personal aside and first-person observations. Vary rhythm on purpose. |
| TikTok, Shorts | Fragments and slang are fine. Match spoken rhythm, not grammar. |
| Instagram | One declarative sentence per slide where possible. Each slide stands alone. |
| Threads, Bluesky | Conversational. Intellectual is fine, academic is not. |
| Podcast | Conversational fragments. Bullets stay keywords. |

## Languages other than English

The pattern list is English. For other languages, skip the lexical lint, keep the specificity pass, and apply the style's `language` setting.

## Reporting

One line in the review: for example "Removed 4 filler phrases, 2 em dash runs and 1 balanced-argument hedge." Give a detailed list only if asked.
