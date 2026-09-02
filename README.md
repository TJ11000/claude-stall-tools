# claude-stall-tools

Claude Code went quiet after a tool call? This dependency-free Python script finds those
gaps in your past session logs, with timestamps. A detector, not a fix.

## Quick start

```bash
python3 stall_scan.py ~/.claude/projects/*/*.jsonl
```

Real output from one session (user text redacted):

```
== 3f9a1c2e  span 10:35:06–21:53:33 JST  events=1379
   [dead-air]     45s gap  10:47:23->10:48:08  after=assistant    then-assistant: '<tool_use:Write>'
   [dead-air]     50s gap  16:13:47->16:14:37  after=tool_result  then-assistant: '<tool_use:Write>'
   [PHANTOM?]     45s gap  10:43:57->10:44:43  after=attachment   then-assistant: ''
   [PHANTOM?]     68s gap  10:44:48->10:45:56  after=tool_result  then-assistant: ''
   [user-after-gap]     96s  18:21:08->18:22:44  after=queue-operation  user: '<redacted>'
```

A clean session prints:

```
   clean (no gaps over threshold after non-user events)
```

## What it flags

| Tag | Meaning |
|---|---|
| `dead-air` | A gap longer than the threshold (default 45s) between a non-user event (e.g. a `tool_result`) and the next assistant event, with **no user input in between** — the model went quiet on its own, not while you were typing. |
| `PHANTOM?` | An assistant turn that arrives after a gap but is nearly empty (< 60 chars, no tool use) — a candidate "woke up and said nothing real" turn. |
| `user-after-gap` | You had to send a message after a non-user gap — often "are you stuck?" — a proxy for a stall you noticed manually. |
| `malformed-retry markers` | Count of `could not be parsed` strings, the retry signature of the tool-call corruption flavor. |

Transcripts usually live under `~/.claude/projects/<encoded-project-path>/*.jsonl`. Tune
`GAP_THRESHOLD` (seconds) near the top of the file if 45s is too tight or too loose for your
machine. Times print in JST by default; change the `JST` constant for your timezone.

## Limits (read before trusting a number)

- **It is wrong in both directions.** A long legitimate think, a slow tool, or a large file
  read looks identical to a stall from the outside — expect false positives on any busy
  session (the sample above has some). And a stall that happens to be shorter than the
  threshold, or that ends with a plausible-looking turn, is missed.
- **It does not detect narrated-but-never-run tools.** If the model *describes* a tool result
  without ever emitting a `tool_use` block, this script won't see it — that check still has to
  be done by hand on the JSONL.
- It reads whatever your transcript format is today. Claude Code changes its JSONL shape
  between versions; if the script prints `no timestamps`, that's why.
- **Silent death is invisible to a count.** If the model emits nothing at all, you catch that
  by noticing a reply that never came — not with this tool.
- **Threshold-dependent.** Everything keys off `GAP_THRESHOLD`; there is no universally
  correct value. Sanity-check against a session you *know* stalled.
- It tells you *where the bug already bit* in a past session. It does not prevent, predict,
  or repair anything. A tripwire that makes a real problem cheaper to find — not a guarantee
  you've found all of it.

## The rest of the repo — contain it, handle it

The stall is one visible symptom of a quieter problem: the control layer under the
automation (tool calls, context, turn-taking) sometimes breaks, and the model barrels ahead
on context it doesn't have. You can't fix that from your side; the cause is upstream. These
are conventions for making the failure louder and cheaper to catch:

- **The "seatbelt" CLAUDE.md snippet** — a runtime, non-coercive instruction that turns the
  dangerous failure (model proceeds on missing context) into the safe one (model stops and
  flags it). → [write-up + snippet](https://gist.github.com/TJ11000/85cf292f65697921b8b2f607c81844a2)
- **[`BRACKET_VALVE.md`](BRACKET_VALVE.md)** — marking unverified values in brackets so a later
  turn has a clean lever to retract a guess instead of defending it. A hypothesis with a small
  observation behind it; the limits are inside.
- **[`PRESSURE_LAYERING.md`](PRESSURE_LAYERING.md)** — *where* you put hard rules changes
  whether the model fabricates: keep the always-loaded base low-pressure, push strict
  constraints down to the per-task layer that can actually check them. Same evidential
  weight as the bracket valve.
- **[`SAFE_READING.md`](SAFE_READING.md)** — once a session *has* broken, reading the wrecked
  transcript to "continue from where it stopped" can spread the corruption to the agent that
  reads it. A method for reading and handing off a broken session without catching the wreck.
- **[`low-pressure-claude-md`](https://github.com/TJ11000/low-pressure-claude-md)** (separate
  repo) — the ideas above as a *complete working* `CLAUDE.md`, the recipe for converting one,
  and an honest record of what did and didn't happen when it ran.

A seatbelt, a dashcam, and a way to clean up. None of it is a fix.

> **Unofficial, third-party. Not affiliated with or endorsed by Anthropic.** Best-effort
> heuristics and conventions, not guarantees — read the limits in each file before trusting it.

## License

CC BY 4.0 — free to use, modify, and redistribute, **with attribution**
(TJ, https://github.com/TJ11000). See [`LICENSE`](LICENSE). Free, and staying free.
