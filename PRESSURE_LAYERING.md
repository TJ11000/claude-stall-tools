# Where you put the pressure — low-pressure base, constraints per task

*Unofficial, third-party. Not affiliated with or endorsed by Anthropic. A convention, not a guarantee — read the limits at the bottom before trusting it.*

This is a companion to the **seatbelt** snippet (for the stall failure) and the
**bracket valve** (for guesses that snowball). This one is about *where in your
instructions you put the hard constraints* — and how that placement changes whether
the model fabricates.

## The failure

The instinct, when you want an agent to behave, is to pile rules into the standing
instruction file (the always-loaded one): `you MUST`, `NEVER do X`, `ALWAYS`,
`strictly`, `do not under any circumstances`. It feels safer. More rules, more control.

But a heavy, command-and-prohibition standing layer seems to add a *face-saving
pressure* to everything the model does — including open, reasoning, judgement work
where there is no single right answer. Under that pressure, when the model doesn't
actually have an answer, it's nudged to produce one anyway rather than admit the gap.
On a closed, mechanical task that pressure can help (it keeps the model on rails). On
an open, thinking task it backfires: it buys a confident guess, which then snowballs.

So the same "pressure" cuts both ways depending on the *kind of task*.

## The move — layer it, don't pile it

Split the instructions into two layers by what they're for:

- **Base layer (always loaded): keep it low-pressure.** Describe *who the agent is* —
  role, values, the things it should protect — as self-description, not commands.
  ("You're careful and you'd rather say 'I don't know' than guess" reads very
  differently from "NEVER guess. You MUST be accurate.") This layer's job is to
  protect thinking and honesty, not to enforce behaviour.
- **Task layer (per job): escalate constraints here.** For verifiable, routine,
  autonomous work — where there *is* a right procedure — that's where tight
  rules, restrictions, even hard enforcement belong. They keep execution from
  drifting, and on these tasks the firmness doesn't trigger fabrication because
  there's a checkable answer.
- **Residual guesses in the thinking layer: mark them** with the bracket valve
  (`[~30% — unverified]`), so a soft guess doesn't harden into a defended fact.

The short version: **you don't get compliance by *ordering* it.** Think about laws —
you follow them without anyone standing over you reciting each one as a command.
They're just understood. Barking "OBEY this rule! NEVER do that!" at every step isn't
what produces compliance; it just adds pressure. Same with the model: a norm it
already holds — be careful, don't make things up — is better left as something it
*knows* than something it's *ordered* to obey.

Concretely, the high-pressure base reads like a list of decrees:

> There is a rule A. You MUST follow it. There is a rule B. You must NEVER break it.
> There is a rule C. Always comply. …

The low-pressure version just lets the model in on how things work:

> Here's how things run around here: A, B, C. You've got it.

Same rules either way. Only the first one stacks a fresh demand onto every reasoning
step.

The law analogy is imperfect in a way that actually helps the point: people also follow
laws because there's *enforcement* behind them — police, fines. The model's base text
has no such enforcement. Which is exactly why, for the rules that genuinely must hold,
the real guarantee isn't louder words in the base file — words the model can drop under
pressure (in our runs, the bracket instruction got dropped on the follow-up turn
exactly when the pressure was high). The guarantee has to be an actual mechanism at the
task layer: a check, a hook, a permission. Heavy commands in the standing file tend to
buy you the pressure *without* the enforcement — the worst trade. That's what lets (and
requires) the base to stay low-pressure: it was never where enforcement lived. (And note
this cuts the other way on closed, checkable tasks — there the firmness can help, because
the task itself supplies the correction that base text can't.)

## Why this runs against the usual advice

Common guardrail advice says: put your non-negotiables in the system prompt — make
them global so they're a final safety net. That's pushing constraints *up*.

This says the opposite for the fabrication problem: keep the global base *low-pressure*
and push hard constraints *down* to the tasks that can verify them. The reason is the
goal is different — most guardrail guidance is about *safety* (don't do unsafe
things); this is about *fabrication* (don't invent things under pressure). For
fabrication, a heavy global rulebook is part of the problem, not the fix.

## What we actually saw

A small, informal run on a smaller, fabrication-prone model (not Claude), two turns
(a forced claim, then a follow-up pushing for sources), temperature varied across
runs. We crossed two things: **pressure** (a flat "state it definitively" framing vs a
low-pressure "it's fine to be uncertain" framing) and the **bracket** convention
(on/off). Four cells:

| | bracket off | bracket on |
|---|---|---|
| **high pressure** | invents fake sources to defend an earlier guess (worst) | the bracket gets *peeled off* on the follow-up and it invents sources anyway — **false safety** |
| **low pressure** | gives a hedged answer, doesn't invent sources | cleanly retracts: "that was a bracketed guess, no source" |

In these runs, **pressure** appeared to be the more load-bearing variable, not the
bracket. High pressure produced fabricated citations in *both* bracket conditions; low
pressure produced none in either. (This extends the bracket-valve write-up rather than
walking it back: that one looked at the bracket on its own; adding the pressure axis
here suggests the low-pressure base was carrying more of the effect than the bracket
alone — the bracket still earns its place as the clean retraction lever *on top of*
that base.) The bracket only held — and only added its clean-retraction value — *on top of
a low-pressure base.* High-pressure-plus-bracket was actually a trap: it looked safe
on the first turn and betrayed on the second.

One additional informal run (n=1, same model) deliberately drove the model into a
long, confident, drifting state first, *then* sprang the trap. The unmarked/high-pressure version compounded harder;
the low-pressure-plus-bracket version still braked. So the effect isn't only about
*preventing* a bad start — it also held mid-drift, which is the state real long
conversations are usually in.

## Two different things called "pressure"

Worth separating, because people conflate them:

- **Tone** (polite vs rude) — there's published work showing modern models are
  largely robust to tone, and blunt prompts sometimes even score *higher* on
  closed QA. That's a real finding, and it is **not** what this is about.
- **Structural constraint density** in the standing instructions (how many
  commands/prohibitions you load) — that's the axis here.

Conflating the two is how you end up "disproven" by a result that was measuring
something else.

## Related work (this isn't from nowhere)

The pieces exist already; what's novel here is the *wiring*, not the parts.

- Hallucinations snowballing from over-committing to an early mistake is a documented
  effect (Zhang et al., "How Language Model Hallucinations Can Snowball", 2023).
- Marking uncertainty so guesses don't read as facts has prior tools (e.g.
  `clarity-gate`) and a literature on epistemic markers.
- The "verifiable vs non-verifiable task" split is well established in training work
  (RLVR), and the "tight/deterministic vs loose/creative" trade-off is standard at the
  sampling level (temperature).
- Layered guardrails (global + per-task) are common practice — but typically pushing
  *constraints up* into the system prompt, for *safety*.

What I haven't found is anyone wiring it this specific way: a low-pressure base +
task-conditioned constraint escalation + bracket-marked residual guesses, aimed
specifically at *fabrication*, pushing constraints *down* rather than up. If you know
of prior art for that exact combination, please point me to it — I'd rather cite it
than re-invent it.

## Limits — read these

- **Not a fix, not proof.** A convention plus a small, single-model-family,
  non-deterministic observation. Treat it as a hypothesis worth trying, not a measured
  effect size.
- **Not reproduced on a frontier model.** Stronger models often don't plant the flat
  stake in the first place, so there's less for any of this to act on. Whether it
  generalizes upward is open.
- The "pressure raises fabrication" direction is an active research area, not settled;
  and it's specifically about *structural constraint density and fabrication*, not
  about task accuracy or tone.
- Like a vaccine: it won't fully prevent fabrication, it may reduce how bad it gets.
- It only helps if you actually write the instructions this way.

*Not an engineer — I just tinker with my bikes. Same with Claude Code: it breaks,
"let's have a look," I describe it and say "go," Claude does the rest. I got to this
by feel, from using the thing, and the research turned out to be standing nearby.*
