# Output file formats

`cw.py output save` and `cw.py validate` read drafts using these conventions. Follow them exactly. A draft that does not match fails or gets warnings that are about format, not content.

Draft files go in `<run>/drafts/<name>.txt`. Saved files become `<run>/<name>.md`.

## Names accepted by `output save --name`

`twitter`, `linkedin`, `newsletter`, `instagram`, `youtube-shorts`, `tiktok`, `threads`, `bluesky`, `podcast`, plus extras that are stored and claims-checked but not validated against a platform: `transformed`, `source-brief`, `calendar`, `hook-variants`, `article`, `show-notes`, `pull-quotes`, `faq`, `announcement`, `email-sequence`. Common aliases such as `x`, `twitter-x`, `ig` and `shorts` are mapped.

## General rules

- Plain text. No front matter. No code fences around the content.
- A line containing only `---` separates units of a multi-part output. Tweets, slides and chained posts are units.
- `[square brackets]` on their own line are visual or stage directions. They are not counted as spoken words, and they are the only place brackets belong in a deliverable.
- No placeholders such as `[insert stat]`, `TODO` or `{{name}}`. The validator fails on them.
- Do not include assistant chatter ("Here is your thread") in the file.

## Per platform

### twitter

```
Unit 1 text.
---
Unit 2 text.
---
Unit 3 text.
```

A single post is one unit with no separator. Each unit is checked against the weighted limit (URLs count as 23, emoji and CJK as 2).

### linkedin

Plain text with blank lines between paragraphs. No markdown.

### newsletter

```
Subject: Specific subject line
Preheader: One line that adds information
CTA: Read the full breakdown

Body paragraphs...

CTA: Reply with your biggest blocker
```

`Subject:` is required. `Preheader:` is optional. `CTA:` lines are counted (maximum two).

### instagram

```
Format: 4:5
---
Slide 1 headline
Up to three short lines
Alt text: Describes the slide for screen readers
---
Slide 2 headline
...
---
Caption: The caption text, with the point in the first 125 characters.
```

Slides are the units that are not `Caption:`. `Format:` and `Alt text:` lines are metadata.

### youtube-shorts

```
Title: Optional title under 100 characters

[Close on the product in the hand]
Spoken line one that is the hook.
[Cut to the screen recording]
Spoken line two.
```

Spoken words are everything outside brackets, `Title:`, `Caption:`, `Description:` and `Hashtags:` lines.

### tiktok

```
Caption: Caption text with 2 to 3 hashtags #topic

[Start mid-action]
Spoken hook within the first ten words.
[Cut]
Next spoken line.
```

### threads and bluesky

Same as twitter. One post, or units separated by `---`.

### podcast

```
SEGMENT 1: Opening
- keyword
- keyword
TRANSITION: one line cue

SEGMENT 2: ...

CTA:
Verbatim spoken call to action.
```

## Extras

- `calendar`: a table of date, platform, file, status. Plain text or Markdown allowed.
- `hook-variants`: a list of 3 to 5 hooks per platform, each labelled with its type.
- `source-brief`: a short summary of the source with core claim, key facts and quotes (with timestamps if the source had them). Useful as input to later runs.
- `transformed`: output of a format conversion.
- `article`, `show-notes`, `pull-quotes`, `faq`, `announcement`, `email-sequence`: long-form pieces from the recipes in `use-cases.md`. Plain Markdown is fine. Pull-quotes must be exact and carry a timestamp when the source has one.

## The run folder

```
content-output/YYYY-MM-DD-<slug>[-v2]/
  source.txt           cleaned source (ingest output)
  drafts/              drafts before validation
  <platform>.md        saved, validated outputs
  manifest.json        hashes, validation and claims results, review status
  review-packet.md     human review card
```

A saved file cannot be overwritten. Revisions go to a new version folder (`output new` with the same title; keep passing the first run's `source.txt` as `--source`). The manifest records each file's hash so the review step can tell if text changed after validation.

`content-output/` is created in the current project. Suggest adding it to `.gitignore` if the user does not want drafts committed.
