# Platform craft guide

How to write for each platform. Limits are not repeated here. They live in `data/platform-specs.json`, are shown by `cw.py specs show <platform>`, and are enforced by `cw.py validate`. This file is about what makes a piece feel native, which code cannot check.

Read the section for each target platform. Output file layout (how to separate tweets or slides) is in `output-formats.md`.

## Rules that apply everywhere

- A piece must stand on its own. Do not write "as I said above" or "in this video".
- Use the source's specifics: its numbers, names, examples, quotes. Generic content is the main failure mode, so if a paragraph could appear in any post on the topic, cut or sharpen it.
- One idea per piece. A piece that tries to cover the whole source covers none of it.
- Compliance beats voice. If the Writing Style pulls against a hard limit, keep the limit and note the trade-off in the review.
- Do not add links, hashtags or emoji the source, style or user did not call for.
- Do not state platform ranking tips as facts. If you mention an algorithm detail to the user, label it with the `kind` shown in `specs show` (official, secondary, craft advice).

## X / Twitter

Format: a single post, or a thread of units separated by `---`.

- Unit 1 is the only one many people will see. It must make sense without the rest, and it must earn the click on "show more".
- Every unit is self-contained enough to be quoted alone.
- No numbering ("1/") unless the style uses it. No "A thread" opener.
- Thread length follows the idea, not a target. A thread under 3 or over 10 units gets a warning from the validator because those are common house limits, not platform rules.
- Links in the body are allowed. Put a link where the reader needs it, not at the end by habit.
- Last unit: the payoff or one clear next step. Not a recap.
- Quality check: would unit 1 stop your own scroll if a stranger posted it?

## LinkedIn

Format: one post. No markdown rendering exists, so `**bold**`, headers, backticks and `[text](url)` links appear as literal characters. Use plain line breaks. If emphasis is essential, use plain words, not Unicode "bold" letters, which screen readers read badly.

- Put the whole hook in the first line. The cut-off before "see more" is not published; roughly 140 characters is safe on mobile, about 210 on desktop.
- Short paragraphs, one to three sentences. White space is the formatting.
- Specific beats inspirational. Cut "excited to share", "humbled", "journey", "thoughts?" closers.
- One call to action. Do not ask for comments to "agree" or "type YES". LinkedIn has said it reduces that kind of bait.
- Hashtags: zero to three, at the end, only if they add discovery value.
- First-person story posts need a real detail (what happened, what it cost, what changed). Without one, write it as a direct claim plus evidence.

## Email newsletter

Format file: `Subject:`, optional `Preheader:`, body, then `CTA:` lines. See `output-formats.md`.

- Subject: specific and honest. 30 to 50 characters is the target. Over 50 is a warning because mobile clips it. Over 78 fails because of the email header line guideline.
- Preheader adds new information. It never repeats the subject.
- Open with the point or a concrete scene in the first three sentences.
- Write to one person. Some informality is correct here. Do not scrub out first-person observations.
- One goal, one primary call to action, optionally repeated once at the end. The `CTA:` line is the button or link text and what the reader gets.
- If it will go to many Gmail or Yahoo addresses, the sending tool must handle one-click unsubscribe and authentication. That is outside the text, so mention it only if the user sends at volume.

## Instagram carousel

Format: slide units separated by `---`, a `Caption:` unit, and alt text. Declare the aspect ratio in the first unit (`Format: 4:5`), because slide 1 sets it for all slides.

- Slide 1 is the headline. It is not a title slide. A bold claim, a specific number, or a question the reader needs answered.
- Each slide earns the next swipe: finish a thought, open the next.
- A headline and up to three short lines per slide. Dense slides get skipped.
- Last slide: one specific action (save, send to someone, a keyword to comment). Say what the reader gets.
- Caption: the first 125 characters show before truncation, so say the point there. Hashtags are capped at 5 on Instagram, and Instagram says they do not increase reach, so use few or none.
- Alt text for each slide is an accessibility requirement worth meeting, and the validator warns if it is missing.

## YouTube Shorts script

Format: spoken lines, with `[square-bracket]` visual directions. Brackets do not count as spoken words. See `output-formats.md`.

- Shorts allow up to 180 seconds, but default to a 60 second script (about 140 words at a normal pace) unless the source needs more. The validator warns above the target and fails above the platform maximum.
- Say the hook in the first three seconds, with no greeting, no channel intro.
- A visual direction every two to four seconds.
- The ending delivers on the hook. A hook that overpromises raises skip-to-end behaviour and hurts retention.
- No links in the script. They belong in the description.
- If the video shows realistic altered or synthetic scenes, YouTube requires disclosure at upload. Mention it in the hand-off.

## TikTok script

Format: spoken lines plus `[visual]` directions and a `Caption:` unit.

- Start mid-thought or mid-action. No "Hey guys", no "In this video".
- The hook lands inside about two seconds of speech, roughly ten words.
- Write for how people talk. Fragments and slang are fine.
- A visual direction every three to five seconds.
- Make the topic searchable: say the subject in the words someone would type.
- Caption: keep it under the platform limit. Use two or three hashtags at most. TikTok publishes no hashtag rule.
- If the video uses realistic AI-generated imagery or voice, TikTok requires a label.

## Threads

Format: one post, or a chain of posts separated by `---`.

- Write for conversation, not broadcast. A question or a position worth answering beats a headline.
- Do not use engagement bait ("comment below"). A specific question or a claim someone can disagree with works better.
- Up to 5 links are allowed. The link preview card appears only on text-only posts.
- One topic tag at most, and only if it names the topic.

## Bluesky

Format: one post of at most 300 graphemes, or a reply chain separated by `---`.

- The community reads closely and dislikes marketing voice. Be plain, specific, a little dry.
- Links are fine and common. Give the link a reason in one clause.
- Every word has to earn its place at 300 graphemes.
- For a divisive take, mention that Bluesky lets the author limit who can reply (threadgate). Say it as an option for the publisher.

## Podcast talking points

Format: keyword bullets grouped by segment, `TRANSITION:` cues between them, and a verbatim `CTA:` section.

- Bullets are keywords or short phrases, not sentences. Over about 12 words a bullet is a script, which the validator fails.
- State the episode's main point in the first segment.
- Mark transitions explicitly so the host can move without improvising bridges.
- The CTA is the only fully written section. Write it the way the host would say it.
- Optional extras on request: chapter titles (Spotify needs at least 3, the first at 00:00, 30 seconds apart), pull-quotes with timestamps, and show notes.

## Quality pass (all platforms)

After drafting, ask silently:

1. Can I name one detail here that only this source could have given?
2. Who is the one person this is for?
3. Does the opening, read cold, make that person keep reading?

If a check fails, fix it. Surface it to the user only if the fix needs information you do not have.
