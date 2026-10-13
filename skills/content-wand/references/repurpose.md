# Converting between content types

Read when the request is a format conversion (podcast to blog, thread to article, notes to newsletter, case study to template), or when a long source must be compressed or expanded. Platform formatting comes after this step, using `platform-writer.md`. Do not format for a platform here.

Write the result to `<run>/drafts/transformed.txt` and save it with `output save --name transformed` so the claims ledger covers it.

## 1. Find the repurposable core

The core is the single insight, claim or story that would survive any format change. Everything else is support.

Test: if only one thing could cross into the new format, which one keeps the piece worth reading? State it in 12 words or fewer.

- No clear core: the source is a grab bag. Ask which idea to build around. Do not guess.
- Two strong cores: it is an editorial decision. Ask once, naming both: "This has two threads, X and Y. Which should anchor the piece?"

Most failed repurposing tries to keep everything. A podcast turned into a thread that covers all eight segments is incoherent. The same podcast with one segment driven to depth is a good thread.

## 2. Classify the distance

| Class | Meaning | Examples |
|---|---|---|
| DIRECT | Similar length and structure | blog to newsletter, thread to LinkedIn post |
| COMPRESS | Long to short | podcast to thread, video to carousel |
| EXPAND | Short to long | notes to blog, one tweet to a newsletter |
| STRUCTURAL | A different kind of document | podcast to ebook outline, case study to template |

If you cannot tell, treat it as DIRECT and say that you assumed it. If the target type is unclear, ask: "What should this become?"

## 3. Apply the class

### DIRECT

Keep the source's structure. Change only what the target needs: register, length, headers. Add no new ideas.

### COMPRESS

- Pick the strongest two or three ideas. The strongest, not the first.
- Build around those and drop the rest. Compression is selection.
- Record what you left out so the user can ask for it: add `omitted themes: ...` to your notes in the review.
- If the source is under about 50 words, compression has nothing to work on. Suggest DIRECT or EXPAND.

### EXPAND

- If the angle is ambiguous, ask one question: "Which aspect should I develop most?" If the user already named it, proceed.
- Aim for roughly three to five times the source length when the user wants a full piece. A single tweet should still become something with real depth.
- A default shape: state the core claim sharper than the source did, add two or three concrete examples that serve the angle, answer the most obvious objection, close one step beyond the opening. Prefer a more natural shape if the source suggests one (narrative arc, problem then result, Q and A, before and after). Vary the shape across jobs.
- The examples must come from the source or from facts the user gives you. Do not invent case studies, numbers or quotes to fill space. If the source is too thin to expand honestly, say so and ask for material.
- Never pad with transitions that carry no information. Never expand every idea equally. Cut the weaker ones.

### STRUCTURAL

The highest-effort class. The target has its own required parts. Make them explicit before writing:

| Target | Required parts |
|---|---|
| Ebook outline | Title, chapter list, one-paragraph summary per chapter, CTA |
| Case study to template | Problem, Approach, Result, Lesson, with placeholders the reader fills |
| Webinar to article | Headline, summary, 3 to 5 sections, pull-quotes with timestamps, CTA |
| Release notes to announcement | What changed, who it affects, what to do, where to learn more (see `use-cases.md`) |

For a template, the placeholders are intentional and belong in the deliverable. They are the one place square-bracket fields are allowed. Tell the user they are fill-ins.

## 4. Fidelity rules

- Do not add ideas the source does not contain or clearly imply.
- Keep quotes exact. If you shorten one, use an ellipsis, do not change words.
- Keep numbers and units exact. "About 40 percent" is not "40 percent".
- Keep names, titles and attributions exact.
- If you cannot tell whether the source states something or you inferred it, leave it out.

## 5. Hand off

Pass the transformed text into Step 5 of the workflow. If the user asked for several platforms, each platform draft starts from the transformed text but must still pass the claims check against the original source.
