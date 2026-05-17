#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  PHOENIX FORGE — NEURAL ARCHITECTURE                             ║
║  Component 6 of 9: CEREBELLUM                                    ║
║  Balance coordinator. No domain left behind.                     ║
║                                                                  ║
║  Install: cp cerebellum.py ~/swarm-platform/                     ║
║  Run:     python3 ~/swarm-platform/cerebellum.py                 ║
╚══════════════════════════════════════════════════════════════════╝

The cerebellum coordinates balance across all domains.
It detects when one domain is pulling ahead while others fall behind.
It detects when the organism is growing lopsided.
It fires serotonin when true balance is achieved.

A platform with 5 perfect apps and 49 broken ones is not a platform.
The cerebellum makes sure evolution lifts all boats.

Emits:
  Serotonin  — balance achieved, organism stable
  Cortisol   — critical imbalance detected (via amygdala relay)

Reads:
  Dopamine   — which domains are excelling (don't neglect them)
  Testosterone — which new territory is being explored
"""

import json
import sys
import statistics
from pathlib import Path
from datetime import datetime

HOME          = Path.home()
SWARM         = HOME / "swarm-platform"
NEURAL_DIR    = SWARM / "neural"
CHAMPIONS     = HOME / "ORGANISM_ARMY/champions"
BALANCE_FILE  = NEURAL_DIR / "cerebellum_balance.json"
CEREBELLUM_L  = NEURAL_DIR / "cerebellum.log"

NEURAL_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SWARM))

from hormone_bus import HormoneBus, OrganismState

# Balance thresholds
IDEAL_STDDEV      = 15.0   # max acceptable standard deviation in scores
CRITICAL_STDDEV   = 40.0   # critical imbalance threshold
MIN_ACCEPTABLE    = 450    # no domain should fall below this
BALANCE_SCORE_MAX = 1.0


class Cerebellum:
    def __init__(self):
        self.bus     = HormoneBus()
        self.state   = OrganismState()
        self.balance = self._load_balance()
        self._log("Cerebellum initialized")

    def _load_balance(self):
        if BALANCE_FILE.exists():
            try:
                return json.loads(BALANCE_FILE.read_text())
            except:
                pass
        return {"history": [], "generation": 0}

    def _save(self):
        BALANCE_FILE.write_text(json.dumps(self.balance, indent=2))

    def coordinate(self, verbose=True):
        """
        Analyze score distribution across all domains.
        Detect imbalances. Emit serotonin if balanced, flag if not.
        Returns coordination report.
        """
        if verbose:
            print("╔══════════════════════════════════════════════════════╗")
            print("║  CEREBELLUM — COORDINATING BALANCE                    ║")
            print("╚══════════════════════════════════════════════════════╝\n")

        # Load all scores
        scores = {}
        FEDERATION = SWARM / "federation"
        for champ_dir in sorted(FEDERATION.iterdir()):
            if not champ_dir.is_dir():
                continue
            champ_file = champ_dir / "node_champion.json"
            if champ_file.exists():
                try:
                    champ = json.loads(champ_file.read_text())
                    total = champ.get("total_score", champ.get("score", 0))
                    if total == 0:
                        ws = champ.get("wisdom_scores", {})
                        wisdom_hit = sum(1 for v in ws.values() if v) * 10
                        total = 540 + wisdom_hit
                    scores[champ_dir.name] = {
                        "total":   total,
                        "tech":    champ.get("score", 275),
                        "human":   champ.get("human_score", 214),
                        "wisdom":  champ.get("wisdom_score", 85),
                    }
                except:
                    pass

        if not scores:
            if verbose:
                print("  No champion scores found. Run evolution first.")
            return {}

        total_scores = [v["total"] for v in scores.values()]
        avg          = statistics.mean(total_scores)
        stddev       = statistics.stdev(total_scores) if len(total_scores) > 1 else 0
        min_score    = min(total_scores)
        max_score    = max(total_scores)
        score_range  = max_score - min_score

        # Balance score: 1.0 = perfect, 0.0 = chaotic
        balance_score = max(0.0, 1.0 - (stddev / CRITICAL_STDDEV))

        # Identify outliers
        below_min    = [(d, s["total"]) for d, s in scores.items()
                        if s["total"] < MIN_ACCEPTABLE]
        top_tier     = [(d, s["total"]) for d, s in scores.items()
                        if s["total"] >= 580]
        mid_tier     = [(d, s["total"]) for d, s in scores.items()
                        if 500 <= s["total"] < 580]
        low_tier     = [(d, s["total"]) for d, s in scores.items()
                        if s["total"] < 500]

        if verbose:
            print(f"  Score distribution across {len(scores)} domains:")
            print(f"  {'─'*50}")
            print(f"  Average:      {avg:.1f}/600")
            print(f"  Std deviation: {stddev:.1f} (ideal: <{IDEAL_STDDEV})")
            print(f"  Range:        {min_score} — {max_score} ({score_range} spread)")
            print(f"  Balance score: {balance_score:.2f}/1.0")
            print(f"  {'─'*50}")
            print(f"  Top tier (≥580): {len(top_tier)} domains")
            for d, s in sorted(top_tier, key=lambda x: -x[1])[:5]:
                bar = "█" * int((s - 450) / 15)
                print(f"    {d:25} {s}/600 {bar}")
            print(f"  Mid tier (500-579): {len(mid_tier)} domains")
            if low_tier:
                print(f"  Low tier (<500):  {len(low_tier)} domains ⚠️")
                for d, s in sorted(low_tier, key=lambda x: x[1])[:5]:
                    print(f"    ⚠️  {d:25} {s}/600 — needs attention")

        # Emit appropriate hormones
        if balance_score >= 0.8 and stddev <= IDEAL_STDDEV:
            # Balanced — emit serotonin
            self.bus.emit(
                "serotonin",
                source="cerebellum",
                intensity=balance_score,
                context={
                    "avg_score":     round(avg, 1),
                    "stddev":        round(stddev, 1),
                    "balance_score": round(balance_score, 2),
                    "message":       "Organism in balance — steady growth",
                }
            )
            if verbose:
                print(f"\n  🟢 Serotonin fired — organism is balanced")

        elif stddev > CRITICAL_STDDEV or below_min:
            # Critical imbalance
            worst_domain = min(scores.items(), key=lambda x: x[1]["total"])
            self.bus.emit(
                "cortisol",
                source="cerebellum",
                intensity=0.85,
                context={
                    "imbalance":      True,
                    "stddev":         round(stddev, 1),
                    "worst_domain":   worst_domain[0],
                    "worst_score":    worst_domain[1]["total"],
                    "action":         f"Urgently evolve {worst_domain[0]} — {worst_domain[1]['total']}/600 drags the platform",
                }
            )
            if verbose:
                print(f"\n  🔴 Cortisol fired — critical imbalance detected")
                print(f"     Worst: {worst_domain[0]} at {worst_domain[1]['total']}/600")

        # Generate balance evolution priorities
        evolution_priorities = []

        # Priority 1: anything below minimum
        for domain, score in sorted(below_min, key=lambda x: x[1]):
            evolution_priorities.append({
                "domain":   domain,
                "score":    score,
                "reason":   f"Below minimum ({MIN_ACCEPTABLE}) — critical",
                "priority": 1,
            })

        # Priority 2: low tier
        for domain, score in sorted(low_tier, key=lambda x: x[1]):
            evolution_priorities.append({
                "domain":   domain,
                "score":    score,
                "reason":   f"Low tier — pulling down platform average",
                "priority": 2,
            })

        # Priority 3: mid tier domains with high-scoring relatives
        from corpus_callosum import DOMAIN_AFFINITY
        for domain, score in mid_tier:
            relatives = DOMAIN_AFFINITY.get(domain, [])
            high_relatives = [r for r in relatives
                              if scores.get(r, {}).get("total", 0) >= 580]
            if high_relatives:
                evolution_priorities.append({
                    "domain":    domain,
                    "score":     score,
                    "reason":    f"Can learn from: {high_relatives[0]} ({scores.get(high_relatives[0],{}).get('total','?')}/600)",
                    "priority":  3,
                })

        # Update state
        self.state.update(
            balance_score=round(balance_score, 2),
            avg_score=round(avg),
        )

        # Save balance history
        self.balance["history"].append({
            "generation":     self.balance["generation"],
            "avg":            round(avg, 1),
            "stddev":         round(stddev, 1),
            "balance_score":  round(balance_score, 2),
            "min_score":      min_score,
            "max_score":      max_score,
            "timestamp":      datetime.now().isoformat(),
        })
        self.balance["history"] = self.balance["history"][-100:]
        self.balance["generation"] += 1
        self.balance["evolution_priorities"] = evolution_priorities[:10]
        self.balance["current_balance"] = round(balance_score, 2)
        self._save()

        report = {
            "domains_analyzed":    len(scores),
            "avg_score":           round(avg, 1),
            "stddev":              round(stddev, 1),
            "balance_score":       round(balance_score, 2),
            "top_tier":            len(top_tier),
            "low_tier":            len(low_tier),
            "below_minimum":       len(below_min),
            "evolution_priorities": evolution_priorities[:5],
        }

        if verbose:
            print(f"\n{'═'*60}")
            print(f"  CEREBELLUM COMPLETE")
            print(f"{'═'*60}")
            print(f"  Balance score:  {balance_score:.2f}/1.0")
            print(f"  Std deviation:  {stddev:.1f} (ideal <{IDEAL_STDDEV})")
            if evolution_priorities:
                print(f"\n  Evolution priorities (next run):")
                for p in evolution_priorities[:3]:
                    print(f"    P{p['priority']}: {p['domain']:25} "
                          f"score={p['score']}  {p['reason']}")
            print(f"\n  Next: python3 ~/swarm-platform/pineal.py")

        self._log(f"Balance={balance_score:.2f} stddev={stddev:.1f} "
                  f"priorities={len(evolution_priorities)}")
        return report

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CEREBELLUM_L, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")


if __name__ == "__main__":
    cerebellum = Cerebellum()
    report     = cerebellum.coordinate(verbose=True)
