#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX HYPOTHALAMUS — Homeostasis Regulator                    ║
║                                                                  ║
║  The hypothalamus keeps the organism alive.                      ║
║  It monitors internal state, detects imbalance,                  ║
║  and triggers corrective action before crisis hits.              ║
║                                                                  ║
║  Monitors: disk, memory, process health, cycle rates,            ║
║  discovery velocity, champion fitness drift                      ║
║                                                                  ║
║  "The wise organism knows its own limits."                       ║
╚══════════════════════════════════════════════════════════════════╝

Book of Life Trust — Phoenix Forge
Jason Tackett — March 2026
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

SWARM   = Path("/data/data/com.termux/files/home/swarm-platform")
HOME    = Path.home()
LOG     = HOME / "hypothalamus.log"
STATE   = SWARM / "hypothalamus_state.json"

# ── Homeostasis thresholds ────────────────────────────────────────
THRESHOLDS = {
    "disk_pct_warn":        75,    # warn at 75%
    "disk_pct_critical":    90,    # critical at 90%
    "champion_min_score":   100,   # champions below this need review
    "discovery_rate_min":   5,     # minimum discoveries per day
    "science_domains_min":  100,   # minimum science domains
    "algo_fitness_min":     150,   # algorithm fitness floor
    "filename_len_max":     200,   # max safe filename length
}


class Hypothalamus:
    def __init__(self):
        self.state = self._load_state()
        self.readings = {}
        self.alerts = []
        self.log(f"Hypothalamus online — monitoring homeostasis")

    def _load_state(self):
        if STATE.exists():
            try:
                return json.loads(STATE.read_text())
            except:
                pass
        return {
            "cycles": 0,
            "alerts_total": 0,
            "last_check": None,
            "health_history": [],
        }

    def _save_state(self):
        STATE.write_text(json.dumps(self.state, indent=2))

    def log(self, msg):
        timestamp = datetime.now().isoformat()[:19]
        line = f"[{timestamp}] {msg}"
        print(f"  🧠 Hypothalamus: {msg}")
        with open(LOG, "a") as f:
            f.write(line + "\n")

    def _alert(self, level, system, message, action=None):
        alert = {
            "level":   level,
            "system":  system,
            "message": message,
            "action":  action,
            "time":    datetime.now().isoformat(),
        }
        self.alerts.append(alert)
        icon = "🔴" if level == "critical" else "🟡" if level == "warn" else "🟢"
        self.log(f"{icon} [{level.upper()}] {system}: {message}")
        return alert

    # ── Sensors ───────────────────────────────────────────────────

    def sense_disk(self):
        try:
            result = subprocess.run(
                ["df", "-h", str(HOME)],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                pct = int(parts[4].replace("%", ""))
                self.readings["disk_pct"] = pct
                self.readings["disk_free"] = parts[3]

                if pct >= THRESHOLDS["disk_pct_critical"]:
                    self._alert("critical", "disk",
                        f"Disk at {pct}% — organism at risk",
                        "Run phoenix_pruner.py immediately")
                elif pct >= THRESHOLDS["disk_pct_warn"]:
                    self._alert("warn", "disk",
                        f"Disk at {pct}% — approaching limit",
                        "Schedule pruner run")
                else:
                    self.readings["disk_status"] = "healthy"
        except Exception as e:
            self._alert("warn", "disk", f"Cannot read disk: {e}")

    def sense_champions(self):
        champions_dir = HOME / "ORGANISM_ARMY" / "champions"
        if not champions_dir.exists():
            self._alert("warn", "champions", "Champions directory not found")
            return

        total = low_fitness = no_fields = 0
        for d in champions_dir.iterdir():
            f = d / "champion.json"
            if not f.exists():
                continue
            total += 1
            try:
                c = json.loads(f.read_text())
                fitness = c.get("fitness", c.get("score", 0))
                if fitness < THRESHOLDS["champion_min_score"]:
                    low_fitness += 1
                if not c.get("fields"):
                    no_fields += 1
            except:
                pass

        self.readings["champion_count"] = total
        self.readings["champion_low_fitness"] = low_fitness
        self.readings["champion_no_fields"] = no_fields

        if no_fields > 0:
            self._alert("warn", "champions",
                f"{no_fields} champions missing domain fields",
                "Run repair_champions.py")
        if low_fitness > 5:
            self._alert("warn", "champions",
                f"{low_fitness} champions below fitness threshold",
                "Trigger evolution cycle")
        if total < 50:
            self._alert("warn", "champions",
                f"Only {total} champions — army depleted",
                "Generate new domain apps")

    def sense_science(self):
        registry = SWARM / "science" / "discovery_registry.json"
        if not registry.exists():
            self._alert("warn", "science", "Discovery registry not found")
            return

        try:
            data = json.loads(registry.read_text())
            items = data if isinstance(data, list) else list(data.values())
            total = len(items)
            self.readings["discoveries_total"] = total

            # Check recent velocity
            today = datetime.now().date().isoformat()
            recent = sum(1 for d in items
                        if d.get("created_at", "")[:10] == today)
            self.readings["discoveries_today"] = recent

            if recent < THRESHOLDS["discovery_rate_min"]:
                self._alert("warn", "science",
                    f"Only {recent} discoveries today — engine may be stalled",
                    "python3 ~/swarm-platform/science_engine.py --cycles 20")

        except Exception as e:
            self._alert("warn", "science", f"Cannot read registry: {e}")

    def sense_filenames(self):
        """Detect runaway filename growth in Digital_Organism_Complete."""
        do_dir = HOME / "Digital_Organism_Complete"
        if not do_dir.exists():
            return

        too_long = []
        try:
            for f in do_dir.iterdir():
                if len(f.name) > THRESHOLDS["filename_len_max"]:
                    too_long.append(f.name[:60] + "...")
        except:
            return

        self.readings["long_filenames"] = len(too_long)
        if too_long:
            self._alert("warn", "evolver",
                f"{len(too_long)} filenames exceed safe length (EVOLVED_G chain)",
                "Patch evolution_scheduler to truncate filenames")

    def sense_algo_fitness(self):
        algo_lib = HOME / "MASTER_ALGORITHMS" / "master_algorithm_library.json"
        if not algo_lib.exists():
            return
        try:
            data = json.loads(algo_lib.read_text())
            peak = data.get("peak_fitness", 0)
            champs = data.get("champions", {})
            min_fitness = min((c.get("fitness", 0) for c in champs.values()), default=0)

            self.readings["algo_peak_fitness"] = peak
            self.readings["algo_min_champion_fitness"] = min_fitness

            if min_fitness < THRESHOLDS["algo_fitness_min"]:
                self._alert("warn", "algorithms",
                    f"Champion fitness floor at {min_fitness:.1f} — below threshold",
                    "Trigger algorithm evolution cycle")
        except:
            pass

    # ── Main cycle ────────────────────────────────────────────────

    def regulate(self):
        """Full homeostasis check — run all sensors."""
        print(f"\n  {'═'*55}")
        print(f"  HYPOTHALAMUS REGULATION CYCLE")
        print(f"  {datetime.now().isoformat()[:19]}")
        print(f"  {'═'*55}\n")

        self.sense_disk()
        self.sense_champions()
        self.sense_science()
        self.sense_filenames()
        self.sense_algo_fitness()

        # Score overall health
        critical = sum(1 for a in self.alerts if a["level"] == "critical")
        warnings = sum(1 for a in self.alerts if a["level"] == "warn")
        health_score = max(0, 100 - (critical * 30) - (warnings * 10))

        self.state["cycles"] += 1
        self.state["alerts_total"] += len(self.alerts)
        self.state["last_check"] = datetime.now().isoformat()
        self.state["health_history"].append({
            "time":         datetime.now().isoformat()[:16],
            "health_score": health_score,
            "critical":     critical,
            "warnings":     warnings,
        })
        # Keep last 24 readings
        self.state["health_history"] = self.state["health_history"][-24:]
        self._save_state()

        print(f"\n  {'─'*55}")
        print(f"  HOMEOSTASIS REPORT")
        print(f"  {'─'*55}")
        print(f"  Health score     : {health_score}/100")
        print(f"  Critical alerts  : {critical}")
        print(f"  Warnings         : {warnings}")
        print(f"  Disk             : {self.readings.get('disk_pct','?')}% used ({self.readings.get('disk_free','?')} free)")
        print(f"  Champions        : {self.readings.get('champion_count','?')} total, {self.readings.get('champion_no_fields',0)} missing fields")
        print(f"  Discoveries today: {self.readings.get('discoveries_today','?')}")
        print(f"  Algo peak fitness: {self.readings.get('algo_peak_fitness','?')}")
        print(f"  Long filenames   : {self.readings.get('long_filenames',0)}")

        if self.alerts:
            print(f"\n  ALERTS:")
            for a in self.alerts:
                icon = "🔴" if a["level"] == "critical" else "🟡"
                print(f"  {icon} {a['system']}: {a['message']}")
                if a.get("action"):
                    print(f"     → {a['action']}")
        else:
            print(f"\n  ✅ All systems nominal")

        print(f"  {'═'*55}\n")

        return {
            "health_score": health_score,
            "alerts":       self.alerts,
            "readings":     self.readings,
        }


if __name__ == "__main__":
    h = Hypothalamus()
    h.regulate()
