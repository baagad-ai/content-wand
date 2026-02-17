# Platform Specifications — 2026 Current

> Loaded on-demand by platform-writer. All specs verified as of February 2026.
> Hard constraints = FAIL if violated. Quality signals = WARN if failing.

---

## Twitter / X

### Hard Constraints
- **Character limit:** 280 per tweet (standard); 25,000 (X Premium long-form post)
- **Thread length:** 3–10 tweets for most content (threads 3x engagement vs. single tweets)
- **External links:** NON-PREMIUM ACCOUNTS: posting external links = near-zero median engagement since March 2026. Links suppressed 50–90% by algorithm. Link placement rule: put URL in a REPLY to tweet 1, NOT in the thread body.
- **Images/media:** Include when possible — media tweets outperform text-only

### Algorithm Signals (2026)
- Replies: 13.5x weight
- Retweets: 20x weight
- Bookmarks: 10x weight
- Likes: 1x weight
- Premium accounts: 2x–4x reach boost
- Recency: top-tier ranking signal — engagement window is hours, not days
- Positive/constructive tone: boosted
- Combative/negative tone: suppressed even with high engagement

### Quality Heuristics
- Tweet 1 must contain: curiosity gap, bold claim, or outcome-first hook
- Test: would tweet 1 get engagement as a standalone post?
- Final tweet: must close the loop / deliver the payoff
- Optimal tweet 1 length: 70–100 characters for maximum interaction rate
- Avoid: "🧵 Thread:" as the opener (overused, no hook value)

---

## LinkedIn

### Hard Constraints
- **Post character limit:** 3,000 characters
- **Visible before "see more":** ~210–220 characters — THIS IS YOUR HOOK ZONE
- **NO native markdown:** `**bold**` renders as literal asterisks. Use Unicode bold if emphasis needed.
- **No headers** with `#` syntax — renders as plain text with the `#` symbol
- **Hashtags:** Count toward character limit (including `#` symbol)
- **Maximum CTAs:** 1 primary
- **Carousel format:** PDF upload only; technical max 300 slides; practical sweet spot: 8–15 slides
- **Carousel dimensions:** 1080×1080px (1:1) or 1080×1350px (4:5)
- **Carousel aspect ratio:** Must be consistent across all slides

### Algorithm Signals (2026)
- Dwell time and saves are high-weight signals
- Native content outperforms external link posts
- First-hour engagement gates wider distribution
- Carousels drive 3× more reach than standard text posts for educational content
- Polls and "ask a question" posts get high early engagement

### Quality Heuristics
- Hook must be in first 210 characters (before "see more" truncation)
- Single-sentence paragraphs dominate high-performing LinkedIn posts
- Short paragraphs (1–3 sentences) with line breaks between each
- One primary CTA — placed at the end of the post
- Avoid: corporate speak, passive voice, hollow openers ("I'm excited to share...")
- High-performing openers: bold statement, contrarian claim, specific data point, personal story

---

## Email Newsletter

### Hard Constraints
- **Subject line:** 30–50 characters; max 7 words
- **Preheader text:** Should complement subject line, not repeat it; can contain secondary CTA
- **Maximum CTAs:** 2 (1 primary above fold + 1 repeat at end) — never more
- **Single goal:** One primary CTA per email
- **Mobile-first:** Single-column layout; minimum 44px touch targets

### Structure (Standard)
1. Header/branding
2. Hook/opener (3–5 sentences — get to the point)
3. Main content block
4. Supporting section (optional)
5. Primary CTA (button format: 45% higher CTR than text links)
6. Footer with unsubscribe

### Quality Heuristics
- Subject line must contain an action verb
- CTA above fold for low-commitment actions; below fold after narrative build for complex offers
- High-converting subject line patterns: number + outcome ("3 ways to..."), curiosity gap, urgency (genuine only)
- Avoid: "checking in", "following up", spam trigger phrases (free, guaranteed, act now)
- Pre-flight check: does reading the first 2 sentences tell you exactly what this email is about?

---

## Instagram Carousel

### Hard Constraints
- **Maximum slides:** 20 (expanded from previous 10-slide limit)
- **Optimal slide count:** 8–10 slides (2.07% engagement rate at 10 slides)
- **Average carousel engagement:** 1.92% (vs. 0.50% Reels, 0.45% single images)
- **Caption limit:** 2,200 characters technical; ~125 characters visible before truncation
- **Square format:** 1080×1080px (1:1)
- **Portrait format:** 1080×1350px (4:5)
- **Aspect ratio lock:** First slide's ratio applies to ALL slides — cannot mix
- **Text overlay limit:** Max 20% of any slide should be text
- **Video slide limit:** 60 seconds; 4GB max

### Structure
- **Slide 1:** Hook — must stop the scroll. Bold claim, striking visual direction, or strong question.
- **Slides 2–N-1:** Body — each slide earns the next swipe. Cliffhanger or incomplete thought at the end of each slide.
- **Final slide:** CTA — clear and specific. For 10-slide carousels: CTA at end only. For 20-slide: CTA mid-carousel AND at end.

### Quality Heuristics
- First slide determines ~80% of carousel performance
- Each slide: 1 headline + max 3 lines of body
- Swipe-cliffhanger pattern: "But there's one more thing..." / "Until slide 5 changed everything..."
- Algorithm rewards swipe completions heavily — engineer for completion, not just slide 1
- Consistent visual style (same fonts, colors, layout) across all slides

---

## YouTube Shorts

### Hard Constraints
- **Maximum length:** 60 seconds
- **Optimal retention length:** 20–45 seconds (entertainment: 15–30s; educational: 35–45s)
- **Aspect ratio:** 9:16 (vertical only)
- **Hook window:** First 3 seconds critical — 50–60% of drop-off happens here
- **Target retention past 3 seconds:** >70%
- **Captions:** Burned-in captions increase retention 15–25% — note this in script

### Script Structure
```
HOOK (0–5 seconds): [Bold claim, curiosity gap, or outcome-first in ≤ 10 words]
BODY (5 sec to near-end): [Build — deliver on the hook's promise]
PAYOFF (final seconds): [Resolution that makes watching worth it]
```

### Quality Heuristics
- Hook must be stated in the first 5 words of the script
- Visual direction note: every 2–4 seconds ("cut to:", "show:", "text overlay:")
- End with a payoff — not a "like and subscribe" — that serves the viewer
- High-performing hook categories:
  - Curiosity gap: "Most people don't know this about [X]"
  - Bold claim: "This changed everything about how I [do X]"
  - Outcome-first: Show result in frame 1, explain how
  - Pattern interrupt: Unexpected visual or statement

---

## Podcast Talking Points

### Hard Constraints
- **Format:** Bullet KEYWORDS only — NOT full sentences. Full sentences cause scripted delivery; keywords allow natural speech.
- **CTA section:** The ONLY verbatim scripted section. Write CTA word-for-word.
- **Hook discipline:** Episode point must be stated within 60 seconds of the outline. Test by reading aloud.
- **Segment timing:** Write target time for each segment. Read aloud with a timer to verify.

### Structure by Episode Length
| Length | Talking Points | Segment Structure |
|--------|---------------|-------------------|
| 10–15 min | 2–3 strong points | Intro (30s) + 2–3 segments (3–5 min each) + Outro (1 min) |
| 20–40 min | 4–6 points | Intro (30s) + segments (5–8 min each) + Recap + Outro |
| 60+ min | 6–8 points | Must include explicit chapter/segment breaks + pacing variation |

### Quality Heuristics
- Transitions between segments must be explicitly noted ("TRANSITION: bridge line")
- Interview question structure: 4–6 questions; first 2 must be open-ended; rest cued from answers
- Segment boundaries: each should have a clear entry and exit point noted
- CTA timing: place at natural pause point — after a segment, before the next, never mid-thought
