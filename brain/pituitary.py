#!/usr/bin/env python3
"""
Phoenix Pituitary Gland
Master regulator â€” reads all brain states, issues directives.
The conductor. Tells every system what to do next.
Book of Life Trust â€” Jason Tackett
"""
import json
from pathlib import Path
from datetime import datetime

HOME  = Path.home()
SWARM = HOME / "swarm-platform"
LOG   = HOME / "logs/pituitary.log"
STATE = SWARM / "pituitary_state.json"

LOG.parent.mkdir(exist_ok=True)

def log(msg):
    ts = datetime.now().isoformat()[:19]
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def read_state(filename):
    path = SWARM / filename
    if path.exists():
        try: return json.loads(path.read_text())
        except: pass
    return {}

def regulate():
    directives = []

    # Read all brain states
    pineal    = read_state("pineal_state.json")
    hormones  = read_state("hormone_bus_state.json")
    prefrontal= read_state("prefrontal_state.json")
    hypo      = read_state("hypothalamus_state.json")
    corpus    = read_state("corpus_callosum_state.json")

    phase      = pineal.get("phase", "growth")
    intensity  = pineal.get("intensity", 0.7)
    cycles     = pineal.get("recommended_cycles", 100)
    mood       = hormones.get("system_mood", "focused")
    dominant   = hormones.get("dominant", "serotonin")
    priority   = prefrontal.get("current_priority", {})
    brain_health = corpus.get("shared_context", {}).get("brain_health", "?")

    # Issue directives based on integrated state
    if phase in ("deep_work", "preparation") and intensity >= 0.8:
        directives.append({
            "target": "science_engine",
            "action": f"--cycles {cycles}",
            "reason": f"Phase {phase} â€” maximize discovery generation",
            "urgency": 0.9
        })
        directives.append({
            "target": "master_algorithm_evolver",
            "action": "run",
            "reason": "High intensity phase â€” evolve algorithms",
            "urgency": 0.8
        })

    if mood == "urgent" or dominant == "cortisol":
        directives.append({
            "target": "meta_evolver",
            "action": "run",
            "reason": "Stress signal â€” evolve rules to improve",
            "urgency": 0.7
        })

    if priority.get("action") == "expand_priority_domains":
        directives.append({
            "target": "forge",
            "action": "generate community domains",
            "reason": priority.get("reason", "Vulnerable populations need coverage"),
            "urgency": 0.9
        })

    # Always run phase4 â€” feedback loop never stops
    directives.append({
        "target": "phase4",
        "action": "run",
        "reason": "Continuous feedback â€” discoveries enrich forge",
        "urgency": 0.6
    })

    # Always run algo injector
    directives.append({
        "target": "algo_injector",
        "action": "run",
        "reason": "Keep domain configs enriched with best algorithms",
        "urgency": 0.5
    })

    directives.sort(key=lambda x: -x["urgency"])

    state = {
        "directives":         directives,
        "directive_count":    len(directives),
        "phase":              phase,
        "mood":               mood,
        "dominant_hormone":   dominant,
        "brain_health":       brain_health,
        "top_priority":       priority.get("action","?"),
        "last_regulation":    datetime.now().isoformat(),
    }

    STATE.write_text(json.dumps(state, indent=2))
    log(f"Brain health: {brain_health}")
    log(f"Phase: {phase} | Mood: {mood} | Dominant: {dominant}")
    log(f"Issued {len(directives)} directives:")
    for d in directives:
        log(f"  â†’ {d['target']}: {d['action']} (urgency={d['urgency']})")
    return state

if __name__ == "__main__":
    log("Pituitary activated â€” master regulation")
    regulate()
    log("Regulation complete")

class PituitaryGland:
    def regulate(self):
        return regulate()

# patch
PituitaryGland.regulate = lambda self, **kw: regulate()

import sys
if sys.platform == 'win32':
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
