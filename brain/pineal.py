#!/usr/bin/env python3
"""
Phoenix Pineal Gland
Circadian rhythm — time awareness and cycle management.
Knows what time it is and adjusts what the organism does.
Heavy evolution at night. Distribution and outreach during day.
Book of Life Trust — Jason Tackett
"""
import json
from pathlib import Path
from datetime import datetime

HOME  = Path.home()
SWARM = HOME / "swarm-platform"
LOG   = HOME / "logs/pineal.log"
STATE = SWARM / "pineal_state.json"

LOG.parent.mkdir(exist_ok=True)

PHASES = {
    range(0,  6): ("deep_work",          1.0, "Heavy evolution — science, algorithms, meta-evolution"),
    range(6,  9): ("morning_synthesis",  0.8, "Consolidate overnight — training data, phase4, commit"),
    range(9, 12): ("distribution",       0.6, "Outreach window — seed apps, partnerships, demos"),
    range(12,14): ("consolidation",      0.5, "Commit and push — preserve all overnight work"),
    range(14,18): ("growth",             0.7, "New domains, features, community distribution"),
    range(18,21): ("review",             0.6, "Gap analysis — verify all systems healthy"),
    range(21,24): ("preparation",        0.9, "Queue overnight runs — set 1000+ cycles"),
}

def log(msg):
    ts = datetime.now().isoformat()[:19]
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def cycle():
    now  = datetime.now()
    hour = now.hour

    phase = "growth"
    intensity = 0.7
    activity  = "General operation"

    for hour_range, (p, i, a) in PHASES.items():
        if hour in hour_range:
            phase, intensity, activity = p, i, a
            break

    # Recommended cycles based on intensity
    recommended_cycles = int(intensity * 200)

    state = {
        "phase":               phase,
        "hour":                hour,
        "intensity":           intensity,
        "activity":            activity,
        "recommended_cycles":  recommended_cycles,
        "day_of_week":         now.strftime("%A"),
        "date":                now.strftime("%Y-%m-%d"),
        "last_cycle":          now.isoformat(),
        "recommendation":      f"{phase} — {activity}",
    }

    STATE.write_text(json.dumps(state, indent=2))
    log(f"Phase: {phase} | Hour: {hour} | Intensity: {intensity}")
    log(f"Activity: {activity}")
    log(f"Recommended cycles: {recommended_cycles}")
    return state

if __name__ == "__main__":
    log("Pineal gland activated — reading circadian rhythm")
    cycle()
    log("Pineal cycle complete")

class PinealGland:
    def tick(self):
        return cycle()

# patch
PinealGland.tick = lambda self, **kw: cycle()
