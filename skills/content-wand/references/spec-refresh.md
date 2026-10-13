# Keeping platform rules current

Platform limits change. The skill never trusts memory for them. All limits sit in `data/platform-specs.json`, and every fact carries a kind, a verification date and a source.

## How freshness is judged

| Kind | Meaning | Review window |
|---|---|---|
| `hard` | The platform enforces it. Content breaks if it is wrong. | 90 days |
| `policy` | An official rule that can change. | 60 days |
| `algorithm` | A ranking signal. Directional only. | 30 days |
| `heuristic` | Craft advice with no official source. | 180 days |

`preflight` lists platforms whose `hard` or `policy` facts are past their window under `specs.stale_hard_or_policy`. A stale fact does not stop work. Tell the user once, in a sentence, and offer a refresh.

## Three ways the data gets updated

1. **Release updates.** New versions of the skill ship new data. Nothing to do.
2. **Signed update feed (opt-in).** If the user turned it on, `specs check-remote` fetches a small feed signed by the maintainer. See below.
3. **Agent-researched refresh.** You look up official sources and propose a change. It is validated by code and applied only after the user says yes.

Local changes live in `specs-overrides.json` in the state directory. The shipped data file is never edited at run time. Every apply saves a snapshot, so `specs rollback` can undo it.

## Signed feed (opt-in)

Off by default. To turn on: `python3 scripts/cw.py pref set update_check on` (the user must approve, since it changes settings). It can also be forced off with the environment variable `CONTENT_WAND_UPDATES=off`.

When on, `python3 scripts/cw.py specs check-remote` makes one request, at most once every 24 hours, to the feed URL in `data/updater.json`. Only that host is allowed. The request carries no identifiers and no content. The feed and its signature are verified with a public key shipped inside the skill. If verification fails, the version is older than what is installed, or the size is wrong, it is discarded.

A valid update is stored as pending and never applied automatically. Show the user the summary from `specs pending` (which facts change, old and new value, source) and apply with `specs apply-remote` only after a yes. `specs discard-remote` drops it.

If `feed_available` in `preflight` is false, the skill shipped without a signing key and the feed is inert. Say so only if the user asks.

## Agent-researched refresh

Use when a fact is stale and no signed update covers it, or the user reports a platform change.

1. Run `python3 scripts/cw.py specs sources <platform>`. It lists the official domains and URL prefixes, the stale facts and the current values.
2. Fetch the official page for each stale fact. Do not use blog posts, social threads or SEO articles for `hard` or `policy` facts. They may be used for `algorithm` or `heuristic` facts and will be marked secondary.
3. Quote the exact sentence from the page that contains the value. The validator checks that a numeric value appears in the quote.
4. Write a proposal file:

```json
{
  "proposal_version": 1,
  "platform": "linkedin",
  "summary": "Re-verified post length limit",
  "changes": [
    {
      "key": "post_char_limit",
      "value": 3000,
      "kind": "hard",
      "source_url": "https://www.linkedin.com/help/linkedin/answer/...",
      "source_quote": "Posts can be up to 3,000 characters.",
      "retrieved_at": "2026-10-13"
    }
  ]
}
```

5. Check it: `python3 scripts/cw.py specs validate-proposal --file proposal.json`. Fix any errors. Rules the validator enforces:
   - `hard` and `policy` facts need an `https` source on an official domain for that platform.
   - Bare user-content hosts (for example a post on x.com) are never official.
   - The value type cannot change, a numeric value must appear in the quote, and `retrieved_at` must be within 3 days.
   - Text fields are scanned for instruction-like content.
   - A change of more than 10 times the old value is flagged as a warning.
6. Show the user a table of old value, new value, source and quote. Ask for approval.
7. On yes: `python3 scripts/cw.py specs apply --file proposal.json`. On a bad result: `specs rollback`.

If an official page cannot be fetched (some help centres block automated requests), say so and leave the fact as it is. Do not substitute a secondary source for a `hard` or `policy` fact.

## After a refresh

Re-run `specs status`. Tell the user what changed in one or two lines. Do not rewrite outputs already approved unless a changed limit makes one non-compliant.

## For maintainers

`scripts/maintainer/feed.py` creates the signing key, builds the feed from the data file, signs and verifies it. `scripts/maintainer/render_specs.py` regenerates `references/platform-specs.md` from the data file. The private key is never stored in the repository. See `docs/ARCHITECTURE.md`.
