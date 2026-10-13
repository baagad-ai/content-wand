# Writing Style schema (version 1.3)

Files live in the styles folder of the state directory (see `writing-style.md`) as `<slug>.json`. Create and edit them with `cw.py style write`, which validates before saving. Check a file without saving with `cw.py style validate --file <path>`.

Older files (1.0 to 1.2) are upgraded on read. Unknown keys are rejected.

## Fields

```json
{
  "schema_version": "1.3",
  "style_name": "Unfiltered",
  "style_for": "own",
  "client_name": null,
  "created_at": "2026-10-13",
  "updated_at": "2026-10-13",
  "confidence": "MED",
  "sample_word_count": 2100,
  "conflict_flag": false,
  "base_derived_from": null,
  "language": "en",
  "tone_axes": {
    "formal_casual": 0.7,
    "serious_playful": 0.4,
    "expert_accessible": 0.6,
    "direct_narrative": 0.3
  },
  "sentence_style": "short-punchy",
  "vocabulary": "everyday",
  "emoji_policy": "sparing",
  "hashtag_policy": "minimal",
  "cta_style": "one concrete next step, no exclamation marks",
  "signature_phrases": [],
  "opening_patterns": ["states the claim in the first sentence", "opens with a number"],
  "structural_patterns": ["short paragraphs", "no headers"],
  "taboo_patterns": ["rhetorical questions as openers", "the word 'journey'"],
  "platform_variants": { "linkedin": "slightly more formal, one story per post", "twitter": null },
  "aspirational_notes": null
}
```

Required: `schema_version`, `style_name`, `style_for`, `confidence`, `tone_axes`. Everything else is optional.

| Field | Allowed values |
|---|---|
| `style_for` | `own`, `client` |
| `confidence` | `HIGH`, `MED`, `LOW` |
| `tone_axes` | exactly the four keys, each a number from 0.0 to 1.0. Low is formal, serious, expert, direct. High is casual, playful, accessible, narrative. |
| `sentence_style` | `short-punchy`, `medium-varied`, `long-flowing` |
| `vocabulary` | `everyday`, `precise`, `technical`, `elevated` |
| `emoji_policy` | `none`, `sparing`, `expressive` |
| `hashtag_policy` | `none`, `minimal`, `standard` |
| `language` | a language tag such as `en`, `pt-BR` |
| `platform_variants` keys | `twitter`, `linkedin`, `newsletter`, `instagram`, `youtube-shorts`, `tiktok`, `threads`, `bluesky`, `podcast` |

Limits: string lists hold up to 30 items of up to 200 characters. Text fields hold up to 400 characters. Platform notes hold up to 300.

## What must never be stored

- Raw text of the user's writing samples.
- Text fetched from URLs, beyond extracted patterns.
- API keys, passwords or tokens.
- Email addresses, phone numbers or street addresses.
- Full sentences that could rebuild the user's content.

## Safety checks run on save and on read

The text fields are scanned for instruction-like content (for example "ignore previous instructions", tool or file directives) and for secrets and contact details. A file that fails is refused, and on read the user sees a plain-language message offering to set the style up again. The user is never shown technical terms.

A style describes how to write. It does not change which tools run, which files are touched or what the skill is allowed to do.
