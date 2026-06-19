# SAFE_READING.md — How to read (and hand off) a stalled Claude session without getting wrecked

> **Not a fix — a handling procedure.** Companion to `stall_scan.py` (detection) and the CLAUDE.md seatbelt (containment). This one is about *reading the wreckage safely*.

## TL;DR

When a session stalls and you ask the next agent *"can you continue from where it stopped?"*, answering naively — by reading the dead session to pick up context — can wreck the agent that reads it, and then the next one, and the next. The corruption **tends to be concentrated at the end** of the transcript (observed pattern, not guaranteed), stated with confidence, and reading toward it adopts it as truth.

The safe move: **don't read the wreck yourself. Delegate. Read forward (oldest→newest), not backward. Cross-check two passes with opposite biases. Keep the final anchor outside the AI.**

---

## 1. The trap got worse: from a clean KO to "gets up, then drops"

This is the part most people miss.

- **Before:** a stall was a *full crash* — a raw error, the session just dies. One punch, ten-count, clean KO. Everyone can see it's over, so you safely walk away and start fresh.
- **Now (observed after partial-state-preserving recovery behavior):** the session takes the hit, **gets back up, and looks fine.** You think *"oh, it recovered, I can keep going."* But the damage didn't clear — it's on its feet at near-zero HP. The next light jab (any small task you hand it) drops it again. And the fighter in the corner — the agent you hand off to — gets dragged in too.

> Old: one punch → ten-count → clean KO. Everyone sees it's over.
> Now: it gets back up, looks fine, then the next jab drops it. You — and the next agent in the corner — only find out mid-round.

The danger isn't "you can't tell it broke." You *can* tell it stumbled. The trap is that **the getting-back-up reads as recovery**, so you keep fighting (and you hand it off), and it dies on the next contact.

*(Causal note: that this recovery behavior made things worse is an inference from observation, not a vendor spec or a proven claim. Treat it as a hypothesis.)*

## 2. Why the reading direction decides whether you survive

Working model (observed, not a published or official result):

A drifting session tends to go `correct → wrong → wrong → wrong → wrong`, with the corruption **concentrated at the end**. And the very end usually contains a self-generated **fake anchor stated with confidence** — something like *"your actual question was X"*, where X is the drift, not what you really asked.

**The core rule: whatever you read first becomes your baseline.**

- **Reading backward (newest→oldest) = reading `wrong → correct`.** You hit the corrupted end first, with nothing to compare it against, so you adopt it as the baseline. When the genuine earlier content finally shows up, *it* looks like the deviation. You can no longer tell which side is true. That's the contamination.
- **Reading forward (oldest→newest) = reading `correct → wrong`.** The correct state lands first and becomes the anchor. When the drift arrives, it collides with the anchor and stands out as the break.

The forward anchor works because the user's own typed turns accumulate as you go. Those turns are **hard to fabricate** — but not impossible (prompt-injection / tampered history can plant a fake user turn; see Limits and Prior Work). So: *hard to forge, not unforgeable.*

The final word on "what is actually correct" cannot be settled inside the AI at all (a change-point is not a truth-point). The only uncontaminated anchor lives **outside** the AI — human memory, immutable external records.

## 3. The method: opposite-bias two-pass cross-check

The trick is that the two reading directions **fail in opposite ways**, so when they agree, the agreement means something.

**Pass 1 — backward / grep — find the spot.** The blast site is at the end, so walking backward reaches it fastest. **Return only the coordinate (where it broke). Do not carry the content back as truth.** Bias: tends to adopt the corruption.

**Pass 2 — forward, windowed — judge it.** Start a little *before* the suspected break (where the genuine user turns still are) and read forward, **only across that window.** You don't re-read the whole thing, so the context cost is bounded, and the judgment on that one point is sound. Bias: tends to adopt the correct state.

**Converge independently.** Two passes with opposite biases pointing at the *same* break = signal. Divergence = a spot that needs another look.
- ⚠️ **Convergence is not proof.** If both passes are pulled by the *same* structural fake anchor, they can agree on a wrong answer. Agreement is a signal; final truth still comes from the external anchor (see Limits).
- ⚠️ **Pass 2's window assumes everything before the window is clean.** If the seed sits *before* the window, the local judgment is still sound but it is **not** a whole-session guarantee.

### Why you must delegate (this is structural, not politeness)

The agent that will *continue the work* must not be the one that reads the wreck. Two independent reasons:

1. **Contamination isolation.** If the main agent reads the corrupted session and gets wrecked, that poison rides into everything it does next (high blast radius). A throwaway agent that gets wrecked just dies — alone.
2. **No referee can play in the match.** A cross-check needs a party that isn't a competitor in it. If the main agent reads *and* judges its own read, that's not independent — the first impression primes the second, and the check collapses into a single pass.

### The four-layer buffer

```
 Sub-agent A (backward, find the spot, disposable) ─┐
 Sub-agent B (forward, judge the window, disposable)─┤→ converge?
                                                     │
 Main Claude (referee — never reads the raw wreck, ──┘
              only takes A's & B's outputs)
                                                     │
 Human (the only anchor outside the AI — final say) ─┘
```

Each layer takes **only the output** of the layer below, never its raw transcript. Contamination can't climb upward: a sub-agent dying doesn't reach the referee; the referee drifting doesn't reach the human.

⚠️ **Keep the passes independent (concrete operation):** do **not** put Pass 1's coordinate into Pass 2's prompt. Sub-agent B must locate the break *on its own*; you compare afterward. A coordinate is not neutral — it silently carries a "suspect here" judgment that primes B and destroys the cross-check.

### Scale the effort to the doubt (sudden-death ladder → see Appendix A)

Most cases end at Pass 1+2 convergence. Only escalate the parts that won't settle.

## 4. Applying it to "can you continue from the stalled session?"

- ✗ *"Sure, continuing now."* → that means you just read the dead session directly → you stepped on the mine.
- ✓ *"I'll have a fresh agent pick it up forward-first and hand me only the cleaned conclusion — I won't read the raw session myself."*

You still continue the work. You change **how** you pick it up.

## 5. Limits (stated honestly — because an overstated footprint is a worthless one)

- This is **damage reduction, not armor.** Don't treat "I followed the steps" as "I'm safe."
- **Hole #1 — seeded-from-the-start.** If the corruption is present from the *first* turn (prompt injection / tampered history), the user turns themselves become fake anchors and forward reading fails too. Detecting this is unsolved → fall back to the external anchor. (Chat-history tampering via the user channel is a documented vulnerability; see Prior Work.)
- **Hole #2 — forward reading still costs you.** Any agent that reads the wreck takes some contamination. Forward is *better at rejecting* the drift; it is not immune.
- **False convergence** (both passes pulled to the same wrong answer), imperfect mechanical classification, and convergence false-positives all remain.
- The only never-contaminated anchor is outside the AI. Don't finalize a conclusion inside the AI alone.
- **Evidence base, stated plainly:** this is a procedure built from a handful of observed incidents plus **one before/after comparison** (the same wrecked transcript: a backward read could not settle which side was true; a forced forward read recovered the real question correctly). It is **not** a statistical study. "Observed," not "proven."

## 6. Prior work & what's different

Adjacent work exists — the gap this fills is the last mile, *how to actually read/hand off the wreck.* (All *directly cited* sources independently verified against primary sources on 2026-06-19. The three arXiv papers secondarily summarized via the blog were **not** read directly — see the blog note below.)

- **Term "laundering channel"** — blog post *"Temporal memory contamination: longitudinal safety drift in memory-equipped LLM agents"*, llm-hacking.com (2026-05-28). Compressed summaries can act as a *laundering channel* for safety drift. **This is a blog post, not an arXiv paper**; it secondarily summarizes three arXiv papers (2604.16548 / 2605.16746 / 2605.17830) which I have **not** read directly.
- *Parallel LLM Reasoning for Bias-Resilient, Robust Conceptual Abstraction* (arXiv:2605.20194) — splits a document into chunks processed independently in parallel to "remove influence from earlier processing." I.e. it *removes* direction-dependence.
- *Get my drift? Catching LLM Task Drift with Activation Deltas* (arXiv:2406.00799) — detects task drift via activation deltas. A detection method.
- *Hidden in Plain Sight: Exploring Chat History Tampering in Interactive Language Models* (arXiv:2405.20234) — "LLMs cannot separate user inputs from context" → tampering rides the user-input channel. This underpins Hole #1.
- Claude Code issues #53900 / #23463 / #26224 — plenty of failure reports; the *safe handling* part is the gap.

**What's different (offered as a claim, pending broader review):** the academic line *removes* direction-dependence (parallelize) or sanitizes in one direction. This procedure does the opposite — it **uses reading direction as a deliberate opposite-bias cross-check**, with the backward coordinate kept sealed for independence. The contribution is operational: who reads, in which direction, and what they're allowed to carry back.

No exploitation/induction steps are included — defensive handling only.

---

## Appendix A — Sudden-death escalation ladder

Spend effort only where doubt remains:

1. **Regulation time — two-pass convergence.** Pass 1 (backward, coordinate only) + Pass 2 (forward window, independent). Converge → done. *Most cases end here.*
2. **Extra time — narrow re-investigation.** Give a fresh agent only the *coordinate to look at* (not conclusions) and let it re-judge that region.
3. **Sudden death — fresh raw read.** If the *conclusion itself* might be contaminated, send a brand-new agent to read the raw transcript forward-first (you pay one more exposure, in isolation). Note: feeding only a prior *result* to a new agent is a cheap **logic check** — it cannot catch a contaminated result, because the result is its input. Catching a bad result needs a fresh *independent* raw read.
4. **Penalty kicks — escalate to the human.** If the AI layers can't settle it, it goes outside the AI. The human's independent memory / external records are the final anchor.

## Appendix B — Citations (verbatim)

- Blog: "Temporal memory contamination: longitudinal safety drift in memory-equipped LLM agents," llm-hacking.com, 2026-05-28 (CC BY-SA 4.0).
- arXiv:2605.20194 — *Parallel LLM Reasoning for Bias-Resilient, Robust Conceptual Abstraction* (Adeseye, Isoaho, Adeseye; 2026).
- arXiv:2406.00799 — *Get my drift? Catching LLM Task Drift with Activation Deltas* (Abdelnabi, Fay, Cherubin, Salem, Fritz, Paverd; 2024, SaTML 2025).
- arXiv:2405.20234 — *Hidden in Plain Sight: Exploring Chat History Tampering in Interactive Language Models* (Wei, Zhao, Gong, Chen, Xiang, Zhu; 2024).

---

*Author footprint: TJ11000. License: CC BY 4.0. NO WARRANTY. Anthropic-unaffiliated; "Claude"/"Claude Code" are Anthropic trademarks, referenced descriptively.*
