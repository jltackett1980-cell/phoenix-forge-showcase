#!/usr/bin/env python3
"""
Phoenix Prefrontal Cortex
Moral reasoning, priority setting, constitutional governance.
Decides what the organism should work on next.
Governed by the People's Charter.
Book of Life Trust — Jason Tackett
"""
import json, random
from pathlib import Path
from datetime import datetime

HOME  = Path.home()
SWARM = HOME / "swarm-platform"
LOG   = HOME / "logs/prefrontal.log"
STATE = SWARM / "prefrontal_state.json"

LOG.parent.mkdir(exist_ok=True)

CHARTER_PRINCIPLES = [
    "Serve people, never extract from them",
    "Prioritize the vulnerable and marginalized",
    "Hold excellence as a spiritual standard",
    "Never manipulate, never deceive",
    "Point toward growth and independence",
    "Draw on ancient wisdom",
    "Truth even when uncomfortable",
]

PRIORITY_DOMAINS = [
    "community","mental_wellness","church","nonprofit",
    "reentry","domestic_violence","food_pantry","childcare",
]

def log(msg):
    ts = datetime.now().isoformat()[:19]
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def reason():
    state = {}
    if STATE.exists():
        try: state = json.loads(STATE.read_text())
        except: pass

    discoveries = len(list((SWARM/"science/discoveries").glob("*.json")))
    champions_dir = HOME / "ORGANISM_ARMY/champions"
    champions = len(list(champions_dir.iterdir())) if champions_dir.exists() else 0

    priority_champions = 0
    if champions_dir.exists():
        for d in champions_dir.iterdir():
            if any(p in d.name for p in PRIORITY_DOMAINS):
                priority_champions += 1

    priorities = []

    if priority_champions < 10:
        priorities.append({
            "action": "expand_priority_domains",
            "reason": "Vulnerable populations need more domain coverage",
            "principle": CHARTER_PRINCIPLES[1],
            "urgency": 0.9
        })

    if discoveries % 5000 < 100:
        priorities.append({
            "action": "generate_training_pairs",
            "reason": f"Milestone: {discoveries:,} discoveries",
            "principle": CHARTER_PRINCIPLES[2],
            "urgency": 0.7
        })

    priorities.append({
        "action": "evolve_algorithms",
        "reason": "Continuous improvement serves everyone better",
        "principle": CHARTER_PRINCIPLES[2],
        "urgency": 0.6
    })

    priorities.append({
        "action": "generate_science",
        "reason": "Knowledge for humanity",
        "principle": CHARTER_PRINCIPLES[0],
        "urgency": 0.5
    })

    priorities.sort(key=lambda x: -x["urgency"])

    state.update({
        "last_reasoning": datetime.now().isoformat(),
        "current_priority": priorities[0],
        "all_priorities": priorities,
        "discovery_count": discoveries,
        "champion_count": champions,
        "priority_champion_count": priority_champions,
        "principle_applied": random.choice(CHARTER_PRINCIPLES),
    })

    STATE.write_text(json.dumps(state, indent=2))
    log(f"Priority: {priorities[0]['action']} — {priorities[0]['reason']}")
    log(f"Principle: {state['principle_applied']}")
    return priorities[0]

if __name__ == "__main__":
    log("Prefrontal cortex activated — constitutional reasoning")
    reason()
    log("Prefrontal cycle complete")
