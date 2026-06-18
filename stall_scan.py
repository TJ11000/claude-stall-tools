#!/usr/bin/env python3
"""Scan session transcripts for stall-bug fingerprints:
- dead air: long gap between a tool_result (or any event) and the next assistant event, no user input between
- phantom: assistant turn after a gap with empty/trivial text
- malformed: 'could not be parsed' retry markers

Companion to the "seatbelt" CLAUDE.md workaround (see README). The seatbelt tries to
contain the bug at runtime; this scanner finds where it already happened, after the fact.

Unofficial, third-party tool. Not affiliated with or endorsed by Anthropic.
Best-effort heuristic — see the "Limits" section of the README before trusting a count.
License: CC BY 4.0 (attribution required). Author: TJ (github.com/TJ11000).
"""
import json, sys, os
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
GAP_THRESHOLD = 45  # seconds

def parse_ts(e):
    ts = e.get("timestamp")
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

def text_of(e):
    msg = e.get("message", {})
    c = msg.get("content", "")
    if isinstance(c, list):
        parts = []
        for x in c:
            if isinstance(x, dict):
                if x.get("type") == "text":
                    parts.append(x.get("text", ""))
                elif x.get("type") == "tool_use":
                    parts.append(f"<tool_use:{x.get('name','?')}>")
                elif x.get("type") == "tool_result":
                    cc = x.get("content", "")
                    if isinstance(cc, list):
                        cc = " ".join(str(y.get("text",""))[:80] for y in cc if isinstance(y, dict))
                    parts.append(f"<tool_result:{str(cc)[:120]}>")
        return " ".join(parts)
    return str(c)

def kind(e):
    t = e.get("type")
    msg = e.get("message", {})
    c = msg.get("content", "")
    if t == "user":
        if isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
            return "tool_result"
        return "user_input"
    return t or "?"

for path in sys.argv[1:]:
    try:
        events = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
    except Exception as ex:
        print(f"!! {path}: {ex}")
        continue

    timed = [(parse_ts(e), e) for e in events]
    timed = [(t, e) for t, e in timed if t]
    if not timed:
        print(f"== {os.path.basename(path)}: no timestamps")
        continue

    start, end = timed[0][0], timed[-1][0]
    print(f"\n== {os.path.basename(path)[:8]}  span {start.astimezone(JST):%H:%M:%S}–{end.astimezone(JST):%H:%M:%S} JST  events={len(timed)}")

    malformed = sum(1 for _, e in timed if "could not be parsed" in text_of(e))
    if malformed:
        print(f"   malformed-retry markers: {malformed}")

    findings = 0
    for i in range(1, len(timed)):
        t_prev, e_prev = timed[i-1]
        t_cur, e_cur = timed[i]
        gap = (t_cur - t_prev).total_seconds()
        if gap < GAP_THRESHOLD:
            continue
        k_prev, k_cur = kind(e_prev), kind(e_cur)
        # gap after user input = TJ idle, not a stall — skip
        if k_prev == "user_input":
            continue
        if k_cur == "assistant":
            txt = text_of(e_cur)
            phantom = (len(txt.strip()) < 60 and "<tool_use" not in txt)
            tag = "PHANTOM?" if phantom else "dead-air"
            print(f"   [{tag}] {gap:6.0f}s gap  {t_prev.astimezone(JST):%H:%M:%S}->{t_cur.astimezone(JST):%H:%M:%S}  after={k_prev}  then-assistant: {txt[:140]!r}")
            findings += 1
        elif k_cur == "user_input":
            txt = text_of(e_cur)
            print(f"   [user-after-gap] {gap:6.0f}s  {t_prev.astimezone(JST):%H:%M:%S}->{t_cur.astimezone(JST):%H:%M:%S}  after={k_prev}  user: {txt[:120]!r}")
            findings += 1
    if not findings and not malformed:
        print("   clean (no gaps over threshold after non-user events)")
