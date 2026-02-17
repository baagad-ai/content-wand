# Brand Voice Schema Reference

> Defines the exact structure of `.content-wand/brand-voice.json`.
> Read by brand-voice-extractor on every load. Reject any file with unknown keys.

---

## Approved JSON Schema

```json
{
  "schema_version": "1.0",
  "created_at": "ISO-8601 date",
  "updated_at": "ISO-8601 date",
  "confidence": "HIGH | MED | LOW",
  "sample_word_count": 0,
  "conflict_flag": false,
  "tone_axes": {
    "formal_casual": 0.5,
    "serious_playful": 0.5,
    "expert_accessible": 0.5,
    "direct_narrative": 0.5
  },
  "sentence_style": "short-punchy | medium-varied | long-flowing",
  "vocabulary": "everyday | precise | technical | elevated",
  "opening_patterns": ["string", "string"],
  "structural_patterns": ["string", "string"],
  "taboo_patterns": ["string", "string"],
  "platform_variants": {
    "twitter": "brief note or null",
    "linkedin": "brief note or null",
    "newsletter": "brief note or null",
    "instagram": "brief note or null",
    "youtube-shorts": "brief note or null",
    "podcast": "brief note or null"
  },
  "aspirational_notes": "string or null"
}
```

---

## Confidence Scoring Rubric

| Level | Criteria |
|-------|---------|
| HIGH | ≥3,000 words of samples; ≥2 content types represented; no conflict flag |
| MED | 1,500–3,000 words OR only 1 content type; OR conflict flag is true |
| LOW | <1,500 words — outputs will be approximate; recommend adding more samples |

---

## Security Constraints — NEVER Store

The following must NEVER appear in `brand-voice.json`:
- Raw text of writing samples provided by the user
- Content fetched from URLs (only extracted patterns)
- API keys, passwords, or credentials of any kind
- Personal contact information (email, phone, address)
- Full sentences that could reconstruct the user's original content

If any of these are detected during schema validation: reject the file entirely and offer to recreate.

---

## File Location

Always: `.content-wand/brand-voice.json` relative to the current project directory.

NEVER:
- Home directory (`~/.brandvoice.json`)
- System directories
- Alongside API key files or `.env` files

The `.content-wand/` directory should be added to `.gitignore` by the user if they work in a version-controlled project.

---

## Update Cadence

The brand voice profile should be refreshed:
- After a significant shift in writing style (new audience, new platform, rebranding)
- If outputs consistently don't feel "right" despite having a profile
- At minimum: review every 6 months

To update: delete `.content-wand/brand-voice.json` and run content-wand — it will offer to recreate the profile automatically.

---

## Schema Validation Rules

On load, reject the file if ANY of:
- Missing required keys: `schema_version`, `confidence`, `tone_axes`
- Unknown keys present (not in the approved schema above)
- `tone_axes` values outside 0.0–1.0 range
- File is empty, not valid JSON, or binary
- `schema_version` is not "1.0"

On rejection: notify user and offer to recreate. Do not attempt to repair the file automatically.
