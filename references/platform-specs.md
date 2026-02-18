# Platform Specifications — 2026 Current

last_verified: 2026-02-18
refresh_after_days: 30

> Loaded on-demand by platform-writer.
> Hard constraints = FAIL if violated. Quality signals = WARN if failing.
>
> **STALENESS CHECK (mandatory before use):** Compare `last_verified` to today's date.
> If age > `refresh_after_days`, run WebSearch to verify current specs before generating.
> Search queries: "[platform] algorithm update 2026", "[platform] character limits 2026"
> Update changed sections and set `last_verified` to today's date before proceeding.

---

## Twitter / X

### Hard Constraints
- **Character limit:** 280 per tweet (standard); 25,000 (X Premium long-form post)
- **Thread length:** 3–10 tweets for most content (threads 3x engagement vs. single tweets)
- **External links:** NON-PREMIUM ACCOUNTS: posting external links = near-zero median engagement since March 2026. Links suppressed 50–90% by algorithm. Link placement rule: put URL in a REPLY to tweet 1, NOT in the thread body.
- **Images/media:** Include when possible — media tweets outperform text-only

### Algorithm Signals (2026 — January Grok update)
- Replies: 13.5x weight
- Retweets: 20x weight
- Bookmarks: 10x weight
- Likes: 1x weight
- **Author reply to someone who replied to you: 150x weight of a like** — highest-value action; prioritize engaging back with replies in the first hour
- Premium accounts: 2x–4x reach boost
- Recency: top-tier ranking signal — engagement window is hours, not days
- Positive/constructive tone: boosted
- Combative/negative tone: suppressed even with high engagement

### Quality Heuristics
- Tweet 1 must contain: curiosity gap, bold claim, or outcome-first hook
- Test: would tweet 1 get engagement as a standalone post?
- Optimal tweet 1 length: 70–100 characters (17% higher engagement than longer openers)
- Short tweets (71–100 chars) consistently outperform long tweets (240+ chars)
- Final tweet: must close the loop / deliver the payoff
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
- **External links:** Reduce organic reach ~60% — place links in first comment rather than post body when possible
- **Carousel format:** PDF upload only; technical max 300 slides; practical sweet spot: 8–15 slides
- **Carousel dimensions:** 1080×1080px (1:1) or 1080×1350px (4:5)
- **Carousel aspect ratio:** Must be consistent across all slides

### Algorithm Signals (2026)
- Dwell time and saves are high-weight signals
- Native content outperforms external link posts
- First-hour engagement gates wider distribution
- **Comments with 5+ words carry significantly more weight than emoji reactions or single-word comments**
- Carousels drive 3× more reach than standard text posts for educational content
- Polls and "ask a question" posts get high early engagement
- Document posts: 2–3x more dwell time than single-image posts

### Quality Heuristics
- Hook must be in first 210 characters (before "see more" truncation)
- Single-sentence paragraphs dominate high-performing LinkedIn posts
- Short paragraphs (1–3 sentences) with line breaks between each
- Long-form posts (1,000–1,300 chars) outperform very short posts
- One primary CTA — placed at the end of the post
- Frame CTA to generate substantive comments ("What's your experience with...?") — earns 5+ word replies
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
- **CTAs phrased as questions ("Ready to try this?") double reply rates vs. statement CTAs**
- CTAs with first-person language (+20% click-through rate over third-person)
- Avoid: "checking in", "following up", spam trigger phrases (free, guaranteed, act now)
- Pre-flight check: does reading the first 2 sentences tell you exactly what this email is about?

---

## Instagram Carousel

### Hard Constraints
- **Maximum slides:** 20 (expanded from previous 10-slide limit)
- **Optimal slide count:** 8–10 slides (2.07% engagement rate at 10 slides)
- **Average carousel engagement:** 1.92% (vs. 0.50% Reels, 0.45% single images) — 4x better than Reels
- **Caption limit:** 2,200 characters technical; ~125 characters visible before truncation
- **Optimal caption length:** ~180 characters (quality target — enough for hook + key point)
- **Square format:** 1080×1080px (1:1)
- **Portrait format:** 1080×1350px (4:5)
- **Aspect ratio lock:** First slide's ratio applies to ALL slides — cannot mix
- **Text overlay limit:** Max 20% of any slide should be text
- **Video slide limit:** 60 seconds; 4GB max

### Algorithm Signals (2026)
- Swipe completions heavily weighted — engineer for completion, not just slide 1 views
- **Comments with 5+ words carry higher weight than emoji or single-word reactions**
- Saves weighted heavily — educational content with high save rate gets amplified
- First slide determines ~80% of carousel performance

### Structure
- **Slide 1:** Hook — must stop the scroll. Bold claim, striking visual direction, or strong question.
- **Slides 2–N-1:** Body — each slide earns the next swipe. Cliffhanger or incomplete thought at the end of each slide.
- **Final slide:** CTA — clear and specific. For 10-slide carousels: CTA at end only. For 20-slide: CTA mid-carousel AND at end.

### Quality Heuristics
- Each slide: 1 headline + max 3 lines of body
- Swipe-cliffhanger pattern: "But there's one more thing..." / "Until slide 5 changed everything..."
- Consistent visual style (same fonts, colors, layout) across all slides
- Frame final CTA to generate a 5+ word comment ("Drop your answer below:")

---

## YouTube Shorts

### Hard Constraints
- **Maximum length:** 60 seconds
- **Optimal retention length:** 20–45 seconds (entertainment: 15–30s; educational: 35–45s)
- **Aspect ratio:** 9:16 (vertical only)
- **Hook window:** First 3 seconds critical — 50–60% of drop-off happens here
- **Target retention past 3 seconds:** >70%
- **Captions:** Burned-in captions increase retention 15–25% — note this in script

### Algorithm Signals (2026)
- **Primary metric: "Engaged Views"** (post-March 2025 shift) — only Engaged Views count toward monetization/YPP eligibility. Standard view count is no longer the primary signal.
- Algorithm first tests with a small seed audience; if retention and engagement are strong, pushes to wider audience
- Percentage of video watched (more important than raw watch time)
- Top performers achieve 80–90% average completion rates
- Replays are high-signal — if viewers replay, algorithm amplifies

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
- Design for seed audience: the hook and first 5 seconds determine whether the algorithm pushes the video
- High-performing hook categories:
  - Curiosity gap: "Most people don't know this about [X]"
  - Bold claim: "This changed everything about how I [do X]"
  - Outcome-first: Show result in frame 1, explain how
  - Pattern interrupt: Unexpected visual or statement

---

## TikTok

### Hard Constraints
- **Video length:** 15 seconds to 10 minutes; optimal: 60s–3min for educational content, 15–30s for entertainment
- **Aspect ratio:** 9:16 (vertical preferred); 1:1 and 16:9 accepted
- **Caption limit:** 2,200 characters (including hashtags)
- **Hashtags:** 3–5 relevant hashtags (more than 5 reduces reach)
- **Script format:** Start mid-action/mid-thought — NO traditional intros or fade-ins
- **Watermarks from other platforms:** TikTok detects and suppresses reposted Reels/Shorts with visible watermarks

### Algorithm Signals (2026)
- **Watch time and completion rate:** PRIMARY signal — percentage watched matters more than raw views
- **Replays:** Very high weight — viewers replaying a video triggers algorithmic amplification
- **Search:** TikTok is now a search engine; search ranking is a direct reach metric — use searchable language
- Niche-specific content: rewarded over broad-appeal content in 2026
- Authentic human content: algorithm detects and deprioritizes AI-generated videos
- Native shopping integration: creators using TikTok Shop features get algorithmic priority
- Longer form (1–3 minutes): gaining algorithmic priority over 15–60s clips for educational content
- Comments drive reach — frame content to generate responses

### Script Structure (TikTok-specific)
```
HOOK (0–2 sec): [Start MID-THOUGHT or mid-action — no intro]
TENSION (2–10 sec): [Create a problem, question, or curiosity gap]
BUILD (10 sec to near-end): [Deliver value — educational, entertainment, or story]
PAYOFF (final sec): [Resolution OR open loop that brings them back]
```

### Quality Heuristics
- Hook must hit in first 1–2 seconds (faster than YouTube Shorts)
- Use searchable language in script and caption — TikTok SEO is real
- Trending audio: using trending sounds gives 2–3x reach boost
- Burned-in subtitles/captions: significantly increase watch time
- Authenticity markers: slightly imperfect audio/lighting outperforms polished AI production
- Engage with comments in first 30 minutes — signals algorithm to push wider
- Avoid: watermarks from Instagram Reels or YouTube (instant suppression)
- Avoid: overly promotional language in first 5 seconds
- Avoid: long intros ("Hey everyone, welcome back to my channel...")

---

## Threads (Meta Platform)

### Hard Constraints
- **Post character limit:** 500 characters
- **Thread:** Up to 25 connected posts (reply chain format — no native thread builder)
- **Links:** One link per post; first link appears as preview card
- **Images:** Up to 10 per post
- **Video:** Up to 5 minutes

### Algorithm Signals (2026)
- **Content neighbourhoods:** AI groups accounts into topic clusters based on recurring keywords/themes — consistency in topic signals which neighbourhood you're in, driving organic distribution
- **Thoughtful replies (5+ words) carry far more weight than emoji reactions**
- **Low-effort engagement actively HURTS visibility** — a flood of "great post" comments suppresses reach
- Meaningful discussion threads boost distribution
- Saves and shares weighted heavily (similar to Instagram)
- Cross-federation: content now shares across Mastodon and other ActivityPub platforms

### Quality Heuristics
- Write for conversation, not broadcast — Threads rewards discussion starters
- Hooks should invite substantive response: "What would you do if..." beats "Here's why..."
- Be consistent in topic/keyword to build neighbourhood authority
- Frame CTAs to generate thoughtful replies, not emoji reactions
- Avoid: generic engagement-bait ("Comment below!")
- Avoid: cross-posting Instagram/Twitter content verbatim — Threads has distinct audience expectations
- Avoid: "Like and share" CTAs — they generate low-quality signals that suppress reach

---

## Bluesky

### Hard Constraints
- **Post character limit:** 300 characters
- **Links:** Full URLs displayed; no need for URL shorteners; links perform well (unlike X)
- **Images:** Up to 4 per post
- **Video:** Limited native video support (as of February 2026)
- **Thread format:** Reply chains (no native thread builder — threads via sequential replies)

### Platform Context (2026)
- 25+ million users; active creator community migrated from X since 2024–2025
- Decentralized (AT Protocol): content visible across federated apps including Mastodon
- Algorithm: User-customizable feeds via "starter packs" — no single opaque algorithm
- No advertising: organic reach is high relative to platform size
- Strong communities: technology, journalism, science, creative writing

### Quality Heuristics
- Longer-form thinking resonates — community values substance over virality
- Link posts perform well (unlike X) — direct article links encouraged
- Tone: conversational, good-faith, intellectually engaged
- Thread-style content works via reply chains — start the thread, reply to yourself to extend
- Use 1–2 topically relevant hashtags (functional but less critical than X)
- Avoid: engagement-bait phrasing — community is sensitive to algorithmic manipulation
- Avoid: Reposting X-native content verbatim (different platform norms)

---

## Beehiiv / Substack Newsletter Platforms

### When to Use (Platform Selection Context)
For platform-writer generating newsletter content, the base format is platform-agnostic. Note the destination platform for any platform-specific guidance.

### Beehiiv (2026)
- 75,000+ newsletters; 350 million monthly readers; 20 billion emails sent in 2025
- **SEO-first architecture:** posts indexed by Google natively — write headlines and intros for search
- Customizable domains with full DNS control; open API with Zapier compatibility
- Analytics: device type, browser, time spent, email engagement all tracked
- Monetization: Stripe fee only — no platform revenue cut on paid subscriptions
- Best for: creators who want SEO reach + newsletter audience simultaneously

### Substack (2026)
- Closed architecture: limits automation and SEO indexing
- Native recommendation algorithm drives cross-newsletter discovery
- Monetization: 10% platform fee on paid subscriptions
- Strong network effects for established writers
- Best for: established writers with existing audience who want discovery via Substack network

### Newsletter Quality Signals (Platform-Agnostic)
- Open rates: 41%+ average in 2026 (well above email marketing norms)
- From name: more important than subject line for repeat open rates
- Send time: Tuesday–Thursday, 8–10am recipient timezone performs consistently
- Reply encouragement ("Reply to this email — I read every one") generates deliverability signal
- Mobile-first: 60%+ of newsletter readers on mobile; keep paragraphs short, CTAs tap-friendly

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
