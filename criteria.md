# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
Search is based on transparent keyword overlap rather than a semantic model,
so a reasonable paraphrase may miss even when the catalog has a related item.
Four of five requires reliable end-to-end behavior while leaving one honest
allowance for vocabulary mismatch or model-service variation.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path is deterministic: an empty Python list is either detected or it is
not, and no model call is required before stopping. Therefore anything below
five of five would indicate a real branch or error-message defect.

---

## 3. The selected listing survives the tool handoff

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->
For five matching queries, `session["outfit_input_item_id"]` equals
`session["selected_item"]["id"]` after the run — in 5 of 5 tries.

**Why this target:**
The loop deliberately reads the selected item back from session state before
calling `suggest_outfit`. IDs are stable and unambiguous, so five of five is a
reasonable target and any mismatch would expose a state-handoff bug.

---

## 4. The fit card contains the facts needed to act

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->
For five matching queries, the returned fit card is two to four sentences and
mentions both the selected listing's price and platform — in at least 4 of 5
tries.

**Why this target:**
Price and platform are the minimum facts needed to find the listing, while a
two-to-four-sentence limit keeps the result usable as a social caption. Because
the wording comes from a probabilistic model, four of five is strict without
pretending every generation will follow formatting perfectly.

---

## 5. Search always respects the price ceiling

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->
Across five searches that include a maximum price, every returned listing has
`price <= max_price` — in 5 of 5 tries.

**Why this target:**
The price comparison is deterministic and the user's budget is a hard
constraint, not a preference. Returning even one item over budget would make
the search tool misleading, so five of five is the appropriate target.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
