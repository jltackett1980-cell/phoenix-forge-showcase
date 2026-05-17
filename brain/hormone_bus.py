#!/usr/bin/env python3
"""
Phoenix Hormone Bus
Chemical signaling — broadcasts urgency, creativity, focus, rest.
Modulates all brain components based on system state.
Book of Life Trust — Jason Tackett
"""
import json, random
from pathlib import Path
from datetime import datetime

HOME  = Path.home()
SWARM = HOME / "swarm-platform"
LOG   = HOME / "logs/hormone_bus.log"
STATE = SWARM / "hormone_bus_state.json"

LOG.parent.mkdir(exist_ok=True)

DEFAULT_HORMONES = {
    "dopamine":   {"role": "reward/motivation",    "level": 0.7},
    "cortisol":   {"role": "stress/urgency",       "level": 0.3},
    "serotonin":  {"role": "stability/wisdom",     "level": 0.8},
    "adrenaline": {"role": "performance/speed",    "level": 0.4},
    "oxytocin":   {"role": "connection/community", "level": 0.9},
    "melatonin":  {"role": "rest/consolidation",   "level": 0.2},
}

def log(msg):
    ts = datetime.now().isoformat()[:19]
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def regulate():
    state = {}
    if STATE.exists():
        try: state = json.loads(STATE.read_text())
        except: pass

    hormones = state.get("hormones", DEFAULT_HORMONES.copy())

    # Read discovery rate
    disc_dir = SWARM / "science/discoveries"
    disc_count = len(list(disc_dir.glob("*.json")))
    prev_count = state.get("prev_discovery_count", 0)
    discovery_rate = disc_count - prev_count

    # Modulate based on discovery rate
    if discovery_rate > 50:
        hormones["dopamine"]["level"] = min(1.0, hormones["dopamine"]["level"] + 0.1)
        hormones["adrenaline"]["level"] = min(1.0, hormones["adrenaline"]["level"] + 0.05)
        log(f"High discovery rate ({discovery_rate}) — dopamine up")
    elif discovery_rate == 0:
        hormones["cortisol"]["level"] = min(0.8, hormones["cortisol"]["level"] + 0.03)
        log("No new discoveries — cortisol rising")

    # Oxytocin boost for community domain work
    champs_dir = HOME / "ORGANISM_ARMY/champions"
    community = 0
    if champs_dir.exists():
        for d in champs_dir.iterdir():
            if any(x in d.name for x in
                   ["community","church","reentry","shelter","nonprofit","ministry"]):
                community += 1
    if community > 0:
        hormones["oxytocin"]["level"] = min(1.0, 0.7 + community * 0.02)

    # Natural oscillation — keeps system feeling alive
    for h in hormones:
        hormones[h]["level"] = max(0.1, min(1.0,
            hormones[h]["level"] + random.gauss(0, 0.02)))

    dominant = max(hormones, key=lambda h: hormones[h]["level"])
    mood = "focused" if hormones["serotonin"]["level"] > 0.7 else \
           "urgent"  if hormones["cortisol"]["level"] > 0.6 else \
           "creative"if hormones["dopamine"]["level"] > 0.8 else "stable"

    state.update({
        "hormones": hormones,
        "dominant": dominant,
        "dominant_role": hormones[dominant]["role"],
        "system_mood": mood,
        "prev_discovery_count": disc_count,
        "community_champion_count": community,
        "last_update": datetime.now().isoformat(),
    })

    STATE.write_text(json.dumps(state, indent=2))
    log(f"Dominant: {dominant} ({hormones[dominant]['role']}) "
        f"level={hormones[dominant]['level']:.2f}")
    log(f"System mood: {mood} | Community champions: {community}")
    return state

if __name__ == "__main__":
    log("Hormone bus activated")
    regulate()
    log("Hormone regulation complete")

class HormoneBus:
    def regulate(self):
        return regulate()

class OrganismState:
    pass

# patch
HormoneBus.read = lambda self, **kw: regulate()

# emit patch
HormoneBus.emit = lambda self, *a, **kw: regulate()

OrganismState.update = lambda self, **kw: None

HormoneBus.read = lambda self, *a, **kw: regulate()
