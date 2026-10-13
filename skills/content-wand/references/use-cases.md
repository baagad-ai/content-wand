# Recipes

Each recipe says what to ask, what to produce, which output names to save and what to watch for. All of them use the same workflow in `SKILL.md`: preflight, style, source, strategy, draft, verify, review. Only the deliverables differ.

Why these recipes: the time in content work is in editing, not generating. People who repurpose do it to stay visible without a second job, and the things they distrust are generic voice, invented facts and sameness. So every recipe is built around source fidelity and fast review.

## Default bundles

Use when the user names a job but no platforms. Offer the bundle in one line and let them change it.

| Source | Default bundle |
|---|---|
| Blog post or essay | LinkedIn post, X thread, newsletter blurb |
| Podcast or video transcript | Pull-quotes, X thread, LinkedIn post, show notes |
| Webinar or talk | Article, LinkedIn post, 3 pull-quotes, FAQ |
| Case study | Case-study pack (below) |
| Release notes or changelog | Tiered announcement kit (below) |
| Rough notes or a voice memo | The one platform they named, written in their style |
| A single strong opinion | LinkedIn post and X post, with hook variants |

## 1. One source to several platforms (the core job)

1. Find the core claim and angle (Step 4). One angle across all platforms keeps the message consistent.
2. Draft each platform from the same angle. Do not paste one draft into each format. Rebuild the hook and structure for each.
3. Save each as its own output. Review them together in one packet.

Watch for: the same sentence appearing in every platform. Vary the opening and the example per platform.

## 2. Hook variants

Ask which platform and how many (default 4). Produce hooks of different types, each labelled, each within the platform's visible-text limit, and recommend one in a line. Save as `hook-variants`. Each hook may use only facts in the source.

## 3. Long-form to media bundle (podcast, video, webinar)

Needs a transcript. If the user gives a video or audio URL with no transcript, ask for the transcript or captions. Do not guess content. SRT and VTT files are supported by `ingest --file` and keep timestamps.

Produce, as the user asks:

- `show-notes`: a two-sentence summary, a bullet list of topics, links mentioned in the source (only those), and chapters with timestamps taken from the transcript. Spotify chapters need at least 3 entries, the first at 00:00, and entries at least 30 seconds apart.
- `pull-quotes`: 3 to 5 exact quotes with the speaker and timestamp. Quotes are copied, never reworded.
- `faq`: 4 to 6 questions the source answers, answered only from the source.
- `article`: a written piece from the strongest segment, using the format conversion rules in `repurpose.md`.
- Short-form scripts (Shorts, TikTok) from one segment each. Do not promise a clip exists. A script is not a video.

Watch for: speaker attribution mistakes in a transcript, and numbers misheard by transcription. Flag anything that looks off instead of fixing it by guess.

## 4. Release notes to tiered announcement kit

For product managers and DevRel. Ask who the audience tiers are if not obvious (existing users, prospects, internal teams).

- `announcement`: one page that leads with what changed for the user, then who it affects, what to do, where to learn more. No internal codenames unless the source uses them publicly.
- `email-sequence` or `newsletter`: a customer-facing note with a single call to action.
- `linkedin` and `twitter`: one post each, focused on the one change users care about most.
- A short internal note (as `transformed`) that says what to tell support and sales.

Rules: include only what the notes say. Never describe a feature as available to everyone if the notes say it is limited, gradual or in preview. Keep version numbers, dates and flag names exact. If the notes contain breaking changes, say so in the first lines.

## 5. Case-study pack

Source: a case study, a customer interview or a results summary.

- Confirm the customer has agreed to be named and to the figures being public. If the source does not say, ask. If unknown, anonymise and say so.
- Produce: a LinkedIn post (outcome-first), an X thread (problem, approach, result), a carousel (one claim per slide), and a template version (`transformed`) with [Problem] [Approach] [Result] [Lesson] fill-ins.
- Every number comes from the source. If a result has no baseline or period in the source, do not state a percentage change.

## 6. Thought-leadership posts (founder, executive, consultant)

- Ask for one opinion or story in the person's words, then write in their style.
- A real detail beats a framework. If they give none, ask one question for a concrete example.
- For a consultant or coach: anonymise client details and ask whether the story may be shared.
- For an executive with a comms team: add a "facts to verify" list to the review notes (names, numbers, dates) so the comms team can check them quickly.

## 7. Newsletter to social

From a published issue, produce the hooks that would make a stranger subscribe, not a summary of the issue. One LinkedIn post and one X post from the strongest section, a short note for Threads or Bluesky, and 3 alternate subject lines if the user wants to resend. Subject lines are checked against length guidance.

## 8. Content calendar

Ask for the date range, posting days and platforms. Produce `calendar`: a table with date, platform, source file, hook, and status. Build the calendar from outputs that exist. Do not schedule pieces that have not been written. Do not state "best times to post" as fact, since there is no reliable platform-published source. Offer the user's own analytics instead. The calendar is a plan. It does not post anything.

## 9. UTM links

When the user wants tracked links, run `cw.py utm <url> --platform <id> --campaign <name> [--content <label>]` for each link instead of writing UTM parameters by hand. Use the user's `utm_default` preference if set. Tell them the final URLs. UTM does not apply to links inside a platform's own bio fields, and some platforms rewrite links. Say that if asked.

## 10. Several clients

Keep one style per client. Create a separate run for each client. Use the client's own source only, and never carry facts from one client into another's run. If a client's style has `language` set, write in it.

## 11. Source fidelity audit

The user pastes a source and a draft written elsewhere, and asks whether the draft is faithful.

1. Save the source to `source.txt` and the draft to a file.
2. Run `cw.py claims --source <source> --output <draft>`.
3. Report each quote, number or link in the draft that is not in the source, and each that is changed. Do not fix without being asked.

## 12. Voice check

The user supplies a draft and a Writing Style and asks if it sounds like them. Compare against the style's patterns and say which patterns match and which do not. Say that this is a judgement, not a measurement, and offer specific edits.

## Things the skill declines or redirects

- Writing a source from nothing (original long-form with no source): offer to research with the user and to treat the notes as the source.
- Generating video, audio or images. It writes scripts and slide text, not media.
- Posting without review.
- Fake testimonials, invented statistics, or quotes attributed to real people who did not say them.
- Impersonating a named real person's voice for deceptive purposes.
- Mass-producing near-duplicate posts for many accounts. Platforms treat that as spam, and the output would be generic anyway.
