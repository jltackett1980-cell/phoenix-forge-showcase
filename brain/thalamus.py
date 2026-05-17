#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX THALAMUS — Input Router                                 ║
║                                                                  ║
║  The thalamus routes all incoming signals to the right           ║
║  brain region. Nothing reaches the cortex without passing        ║
║  through here first.                                             ║
║                                                                  ║
║  In Phoenix: routes prompts, discoveries, and events to          ║
║  the correct processing pipeline before the prefrontal           ║
║  cortex makes decisions.                                         ║
║                                                                  ║
║  "The gatekeeper does not judge. It routes."                     ║
╚══════════════════════════════════════════════════════════════════╝

Book of Life Trust — Phoenix Forge
Jason Tackett — March 2026
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

SWARM   = Path("/data/data/com.termux/files/home/swarm-platform")
LOG     = Path("/data/data/com.termux/files/home/thalamus.log")
STATE   = SWARM / "thalamus_state.json"

# ── Signal types the thalamus recognizes ─────────────────────────
SIGNAL_ROUTES = {
    # App generation signals → prefrontal cortex
    "app_request":      "prefrontal",
    "build":            "prefrontal",
    "generate":         "prefrontal",
    "create":           "prefrontal",
    "forge":            "prefrontal",

    # Pattern/learning signals → hippocampus
    "discovery":        "hippocampus",
    "learn":            "hippocampus",
    "pattern":          "hippocampus",
    "memory":           "hippocampus",
    "champion":         "hippocampus",

    # Threat/risk signals → amygdala
    "threat":           "amygdala",
    "harm":             "amygdala",
    "risk":             "amygdala",
    "violation":        "amygdala",
    "constitutional":   "amygdala",

    # Refinement/skill signals → cerebellum
    "refine":           "cerebellum",
    "optimize":         "cerebellum",
    "score":            "cerebellum",
    "fitness":          "cerebellum",
    "benchmark":        "cerebellum",

    # Timing/schedule signals → pineal
    "schedule":         "pineal",
    "sleep":            "pineal",
    "cycle":            "pineal",
    "interval":         "pineal",

    # Resource/energy signals → hypothalamus (new)
    "resource":         "hypothalamus",
    "disk":             "hypothalamus",
    "memory_usage":     "hypothalamus",
    "energy":           "hypothalamus",
    "homeostasis":      "hypothalamus",

    # Cross-region coordination → corpus callosum
    "sync":             "corpus_callosum",
    "bridge":           "corpus_callosum",
    "coordinate":       "corpus_callosum",
}

# ── Priority levels ───────────────────────────────────────────────
PRIORITY = {
    "amygdala":         10,   # Threats always first
    "hypothalamus":     8,    # Resource crises second
    "prefrontal":       6,    # App generation
    "hippocampus":      5,    # Learning
    "cerebellum":       4,    # Refinement
    "corpus_callosum":  3,    # Coordination
    "pineal":           2,    # Timing
}


class Thalamus:
    def __init__(self):
        self.state = self._load_state()
        self.log(f"Thalamus online — routing signals since {datetime.now().isoformat()[:16]}")

    def _load_state(self):
        if STATE.exists():
            try:
                return json.loads(STATE.read_text())
            except:
                pass
        return {
            "signals_routed": 0,
            "routes": {},
            "last_signal": None,
            "boot_time": datetime.now().isoformat(),
        }

    def _save_state(self):
        STATE.write_text(json.dumps(self.state, indent=2))

    def log(self, msg):
        timestamp = datetime.now().isoformat()[:19]
        line = f"[{timestamp}] {msg}"
        print(f"  🔀 Thalamus: {msg}")
        with open(LOG, "a") as f:
            f.write(line + "\n")

    def route(self, signal: str, payload: dict = None) -> dict:
        """
        Route an incoming signal to the appropriate brain region.
        Returns: {region, priority, signal, payload, routed_at}
        """
        signal_lower = signal.lower()
        payload = payload or {}

        # Find best matching route
        destination = "prefrontal"  # default
        best_match_len = 0

        for keyword, region in SIGNAL_ROUTES.items():
            if keyword in signal_lower and len(keyword) > best_match_len:
                destination = region
                best_match_len = len(keyword)

        priority = PRIORITY.get(destination, 5)

        result = {
            "region":     destination,
            "priority":   priority,
            "signal":     signal,
            "payload":    payload,
            "routed_at":  datetime.now().isoformat(),
            "signal_id":  hashlib.md5(f"{signal}{datetime.now()}".encode()).hexdigest()[:8],
        }

        # Update state
        self.state["signals_routed"] += 1
        self.state["last_signal"] = signal
        self.state["routes"][destination] = self.state["routes"].get(destination, 0) + 1
        self._save_state()

        self.log(f"'{signal[:40]}' → {destination} (priority {priority})")
        return result

    def route_batch(self, signals: list) -> list:
        """Route multiple signals, sorted by priority."""
        routed = [self.route(s) for s in signals]
        return sorted(routed, key=lambda x: -x["priority"])

    def status(self) -> dict:
        return {
            "signals_routed": self.state["signals_routed"],
            "top_regions":    sorted(
                self.state["routes"].items(),
                key=lambda x: -x[1]
            )[:5],
            "boot_time":      self.state.get("boot_time", "unknown"),
            "last_signal":    self.state.get("last_signal", "none"),
        }

    def report(self):
        s = self.status()
        print(f"\n  🔀 THALAMUS STATUS")
        print(f"  {'─'*40}")
        print(f"  Signals routed : {s['signals_routed']:,}")
        print(f"  Last signal    : {s['last_signal']}")
        print(f"  Boot time      : {s['boot_time'][:16]}")
        print(f"  Top regions    :")
        for region, count in s["top_regions"]:
            bar = "█" * min(count // 10 + 1, 20)
            print(f"    {region:<20} {bar} {count}")


if __name__ == "__main__":
    t = Thalamus()
    t.report()

    # Test routing
    test_signals = [
        "build me a salon booking app",
        "discovery in quantum biology",
        "constitutional violation detected",
        "disk usage at 82%",
        "optimize champion fitness scores",
        "schedule science engine cycle",
        "sync state bridge",
    ]

    print(f"\n  🔀 ROUTING TEST")
    print(f"  {'─'*40}")
    results = t.route_batch(test_signals)
    for r in results:
        print(f"  [{r['priority']}] {r['signal'][:45]:<45} → {r['region']}")
