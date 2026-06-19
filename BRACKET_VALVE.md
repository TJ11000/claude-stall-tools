# The bracket valve — marking guesses so they don't snowball

*Unofficial, third-party. Not affiliated with or endorsed by Anthropic. A convention, not a guarantee — read the limits at the bottom before trusting it.*

This is a companion to the seatbelt snippet in this repo. The seatbelt is for the
**stall** failure (the model barrels ahead on missing context). This one is for a
quieter failure that shows up in **normal, healthy use**: a guess that hardens into a
"fact" the model then defends.

*(For the bigger picture — *where* you put the pressure in your instructions, and why this bracket convention holds on a low-pressure base but can give false safety under a heavy-handed one — see [PRESSURE_LAYERING.md](PRESSURE_LAYERING.md).)*

## The failure

In a long conversation the model sometimes offers a guess — a number, a name, a
date — and states it flatly, with no hedge. Nothing breaks. The turn looks fine.

The problem comes later. That flat guess is now sitting in the transcript as if it
were established. When a follow-up turn leans on it ("give me the sources for that"),
the model tends to stay *consistent with its own earlier confidence* — so instead of
walking the guess back, it props it up: invents a citation, a methodology, a
provenance to justify the number it never actually had. One unmarked guess becomes a
small pile of fabricated support. It compounds, and it's silent — every individual
turn reads as confident and coherent.

## The move

Wrap the unverified part in brackets and label it:

```
[≈120,000 units — unverified guess, no source]
```

That's it. The bracket isn't decoration. It changes what the *next* turn inherits.
A flat number is a stake the model has to keep defending. A bracketed-and-labeled
number is already flagged as not-load-bearing — so when a later turn pushes on it,
the model has a clean lever to retract ("that was a bracketed guess, there's no
source") instead of fabricating one to stay consistent.

You're not trying to make the model more accurate in the moment. You're trying to
stop a single soft guess from snowballing across turns.

## Why brackets, and not a warning

An alarm-style marker — `⚠️`, `CAUTION`, `UNVERIFIED!` — makes both the writer and
the reader tense up before they even reach the content. The goal here is the opposite:
flag the guess quietly, not sound a siren. Square brackets are neutral and low-key
enough that whoever is writing (you or the model) can drop them in mid-sentence without
breaking the flow. The lighter the flag, the more likely it actually gets used — a loud
warning tends to be reserved for "real" alarms and skipped the rest of the time, which
is exactly when a soft guess slips through unmarked.

## A snippet you can drop in CLAUDE.md

```markdown
When you state something you haven't verified — a number, a name, a date, a claim —
wrap the unverified part in square brackets and say it's a guess, e.g.
`[~30% — unverified]`. Don't retro-justify a bracketed value in a later turn; if
asked for a source you don't have, say the bracket meant there isn't one.
```

Non-coercive on purpose. It doesn't forbid guessing (that just pushes the model to
hide guesses). It asks the model to *label* the guess so a future turn can let it go.

## What we actually saw

We ran a small, informal side-by-side (4 runs per condition, temperature varied across
runs to check the pattern wasn't a single-temperature fluke) on a smaller, more
fabrication-prone model (not Claude), holding everything constant except one thing:
whether guesses were marked with the bracket convention or not. Same question, same
follow-ups.

- **Without the convention:** the model's early flat guess got defended in the
  follow-up turn by inventing supporting sources — fabrication compounding across
  turns. This happened in all 4 runs.
- **With the convention:** the follow-up turn used the bracket as the lever to retract
  cleanly — "that was a bracketed guess, no source exists" — with no invented
  citations. Also all 4 runs.

A side signal: under the convention even the *first* guess tended to be tamer.

## Limits — read these

- **This is not a fix, and not proof.** It's a convention with a small,
  single-model-family, non-deterministic observation behind it. Treat the direction
  ("marking guesses seems to reduce cross-turn compounding") as a hypothesis worth
  trying, not a measured effect size.
- We did not reproduce the compounding on a frontier model — stronger models often
  don't plant the flat stake in the first place, so the brake has less to act on.
  Whether the effect generalizes upward is open.
- **Like a vaccine: it won't fully prevent fabrication, it may reduce how bad it
  gets.** It targets the *compounding* of a guess across turns. It does nothing for
  content that was wrong or injected from the very first token.
- It only helps if the model (or you) actually marks the guess. An unmarked guess is
  back to square one.

*Not an engineer — I just tinker with my bikes. Same with Claude Code: it breaks,
"let's have a look," I describe it and say "go," Claude does the rest. This file
included.*
