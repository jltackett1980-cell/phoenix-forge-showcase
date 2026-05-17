#!/usr/bin/env python3
"""
Phoenix Corpus Callosum
Synchronizes all brain components — shares state across the whole brain.
Book of Life Trust — Jason Tackett
"""
import json
from pathlib import Path
from datetime import datetime

HOME  = Path.home()
SWARM = HOME / "swarm-platform"
LOG   = HOME / "logs/corpus_callosum.log"
STATE = SWARM / "corpus_callosum_state.json"

LOG.parent.mkdir(exist_ok=True)

BRAIN_STATE_FILES = [
    "prefrontal_state.json",
    "amygdala_state.json",
    "hippocampus_state.json",
    "thalamus_state.json",
    "hypothalamus_state.json",
    "cerebellum_state.json",
    "hormone_bus_state.json",
    "pineal_state.json",
    "pituitary_state.json",
]

def log(msg):
    ts = datetime.now().isoformat()[:19]
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def synchronize():
    unified = {
        "sync_time": datetime.now().isoformat(),
        "components": {},
        "shared_context": {}
    }

    for state_file in BRAIN_STATE_FILES:
        path = SWARM / state_file
        component = state_file.replace("_state.json", "")
        if path.exists():
            try:
                data = json.loads(path.read_text())
                unified["components"][component] = {
                    "online": True,
                    "last_update": data.get(
                        "last_update",
                        data.get("last_reasoning",
                        data.get("sync_time", "?"))
                    )
                }
            except:
                unified["components"][component] = {"online": False, "error": "parse_failed"}
        else:
            unified["components"][component] = {"online": False}

    online = sum(1 for v in unified["components"].values() if v.get("online"))
    total  = len(BRAIN_STATE_FILES)

    # Read discovery count for shared context
    disc_dir = SWARM / "science/discoveries"
    disc_count = len(list(disc_dir.glob("*.json")))

    # Read prefrontal priority for shared context
    pre_path = SWARM / "prefrontal_state.json"
    current_priority = "unknown"
    if pre_path.exists():
        try:
            pre = json.loads(pre_path.read_text())
            current_priority = pre.get("current_priority", {}).get("action", "unknown")
        except: pass

    # Read previous sync count
    prev_sync = 0
    if STATE.exists():
        try:
            prev_sync = json.loads(STATE.read_text()).get(
                "shared_context", {}).get("sync_count", 0)
        except: pass

    unified["shared_context"] = {
        "brain_health": f"{online}/{total} components online",
        "discovery_count": disc_count,
        "current_priority": current_priority,
        "sync_count": prev_sync + 1,
    }

    STATE.write_text(json.dumps(unified, indent=2))
    log(f"Brain sync complete: {online}/{total} online")
    log(f"Priority in context: {current_priority}")
    log(f"Discoveries in context: {disc_count:,}")
    return unified

if __name__ == "__main__":
    log("Corpus callosum — synchronizing brain")
    state = synchronize()
    log(f"Health: {state['shared_context']['brain_health']}")

class CorpusCallosum:
    def transfer(self):
        return synchronize()

# patch
_orig_cc_transfer = CorpusCallosum.transfer
CorpusCallosum.transfer = lambda self, **kw: synchronize()

DOMAIN_AFFINITY = {}
