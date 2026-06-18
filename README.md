# claude-stall-tools

Small, honest tools for the part of Claude Code nobody's looking at: **the control layer
underneath the automation.**

Everyone's racing to *generate* more with AI. Meanwhile the layer that's supposed to keep
the agent on the rails — tool calls, context, turn-taking — sometimes quietly breaks: the
model stalls after a tool call, leaks raw tool markup instead of running it, or fabricates
a result (or a whole answer) that was never really there. You can't fix that from your
side; the cause is upstream. But you can **see it** and **contain it.**

This repo is two pieces:

- **`stall_scan.py`** — *see it.* Scans your session transcripts after the fact and shows
  where the stall fingerprints actually showed up.
- **the "seatbelt" CLAUDE.md snippet** — *contain it.* A runtime, non-coercive instruction
  that turns the dangerous failure (model barrels ahead on missing context) into the safe
  one (model stops and flags it). →
  [seatbelt write-up + snippet](https://gist.github.com/TJ11000/85cf292f65697921b8b2f607c81844a2)

Neither is a fix. They're instruments: measure the breakage, make the failure louder and
cheaper to catch. **Not a fix — just a seatbelt and a dashcam.**

> **Unofficial, third-party. Not affiliated with or endorsed by Anthropic.** These are
> best-effort heuristics and conventions, not guarantees — read the limits before trusting
> either one.

---

## stall_scan.py — find the stall in your logs

A tiny, dependency-free Python script that scans Claude Code session transcripts
(`.jsonl`) for the fingerprints of the intermittent stall / phantom-output bug and prints
where they happened, with timestamps. A **detector**, not a fix and not a preventer — it
tells you *where the bug already bit* in a past session.

### What it flags

| Tag | Meaning |
|---|---|
| `dead-air` | A gap longer than the threshold (default 45s) between a non-user event (e.g. a `tool_result`) and the next assistant event, with **no user input in between** — i.e. the model went quiet on its own, not while you were typing. |
| `PHANTOM?` | An assistant turn that arrives after a gap but is nearly empty (< 60 chars, no tool use) — a candidate "woke up and said nothing real" turn. |
| `user-after-gap` | You had to send a message after a non-user gap — often "are you stuck?" — a proxy for a stall you noticed manually. |
| `malformed-retry markers` | Count of `could not be parsed` strings, the retry signature of the tool-call corruption flavor. |

### Usage

```bash
python3 stall_scan.py /path/to/your/*.jsonl
```

Claude Code transcripts usually live under
`~/.claude/projects/<encoded-project-path>/*.jsonl`. Point the script at one or many:

```bash
python3 stall_scan.py ~/.claude/projects/*/*.jsonl
```

It prints, per file, the session time span, any malformed-retry count, and one line per
finding. A clean session prints `clean (no gaps over threshold after non-user events)`.

Tune `GAP_THRESHOLD` (seconds) near the top of the file if 45s is too tight or too loose
for your machine. Times are printed in JST (Japan Standard Time, UTC+9) by default; change the `JST`
constant near the top of the file for your timezone.

### Limits (read this before trusting a number)

This is a best-effort heuristic over timestamps and shapes. It is **wrong in both
directions** and is not a substitute for your own eyes:

- **False positives.** A long gap can just be a slow-but-healthy turn, a big tool result,
  or thinking split into empty events that resolve a second later. `dead-air` means
  *suspicious gap*, not *confirmed stall*. Read the surrounding lines before concluding.
- **Silent death is invisible to a count.** If the model emits *nothing at all*, you still
  catch that by noticing a reply that never came, not by this tool.
- **It can't see fabrication.** A confident made-up answer with normal timing leaves no
  fingerprint here. This finds *stalls and gaps*, not hallucinations.
- **Format-dependent.** It reads the current Claude Code `.jsonl` event shape. If that
  format changes upstream, the parser may silently under-report. Sanity-check against a
  session you *know* stalled.
- **Threshold-dependent.** Everything keys off `GAP_THRESHOLD`. There is no universally
  correct value.

In short: a tripwire that makes a real problem cheaper to find — not a guarantee you've
found all of it.

---

## License

CC BY 4.0 — free to use, modify, and redistribute, **with attribution**
(TJ, https://github.com/TJ11000). See [`LICENSE`](LICENSE).

Free, and staying free. No catch, nothing gated.
</content>
