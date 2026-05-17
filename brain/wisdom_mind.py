#!/usr/bin/env python3
"""
Phoenix Forge — Wisdom Mind
Book of Life Ministries · Book of Life Trust
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime

HOME = Path.home()
PLATFORM = HOME / "swarm-platform"
STATE_FILE = PLATFORM / "neural" / "wisdom_mind_state.json"
LOG_FILE = HOME / "logs" / "wisdom_mind.log"

# Import I Ching
ICHING_AVAILABLE = False
try:
    from iching_engine import cast_hexagram, HEXAGRAMS
    ICHING_AVAILABLE = True
except ImportError:
    pass

# Import Codex
CODEX_AVAILABLE = False
try:
    from wisdom_codex import get_codex
    CODEX_AVAILABLE = True
except ImportError:
    pass

class WisdomMind:
    """The forge's wisdom consciousness."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.state = self._load_state()
        self._generation_count = self.state.get("generation_count", 0)
        self._session_hexagrams = self.state.get("session_hexagrams", [])
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._log("wisdom_mind_activated", "The council is assembled.")
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def _load_state(self):
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text())
            except:
                pass
        return {"generation_count": 0, "session_hexagrams": []}
    
    def _save_state(self):
        self.state["generation_count"] = self._generation_count
        self.state["session_hexagrams"] = self._session_hexagrams[-100:]
        self.state["last_update"] = time.time()
        try:
            STATE_FILE.write_text(json.dumps(self.state, indent=2))
        except:
            pass
    
    def _log(self, event, detail):
        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.now().isoformat()} | {event} | {detail}\n")
        except:
            pass
    
    def read_moment(self, question=""):
        """Cast a hexagram for the current moment."""
        if not ICHING_AVAILABLE:
            return {"hexagram_number": 0, "hexagram_english": "I Ching not available", "available": False}
        
        try:
            result = cast_hexagram(question)
            self._session_hexagrams.append({
                "question": question[:100],
                "hexagram": result.get("hexagram_number", 0),
                "timestamp": time.time(),
            })
            self._save_state()
            return result
        except Exception as e:
            self._log("read_moment_error", str(e))
            return {"hexagram_number": 0, "hexagram_english": "Error", "error": str(e)}
    
    def what_does_the_tao_say(self, situation):
        teachings = {
            "beginning": "A journey of a thousand miles begins with a single step.",
            "service": "Water benefits all things and does not compete.",
            "restraint": "The usefulness is in the emptiness.",
            "empowerment": "When the work is done, the people say: we did it ourselves.",
        }
        return teachings.get(situation, "Let the situation show you what it needs.")
    
    def what_does_krishna_say(self, situation):
        teachings = {
            "action": "You have the right to act. Not to the fruits. Build because it is right.",
            "quality": "The wise do the same work without attachment.",
            "empathy": "Compare others' happiness with your own.",
        }
        return teachings.get(situation, "Act as a matter of duty, without attachment.")
    
    def get_status(self):
        return {
            "active": True,
            "iching_available": ICHING_AVAILABLE,
            "codex_available": CODEX_AVAILABLE,
            "generation_count": self._generation_count,
            "session_hexagrams": len(self._session_hexagrams),
            "last_update": self.state.get("last_update"),
        }

if __name__ == "__main__":
    mind = WisdomMind.instance()
    print("=" * 50)
    print("Wisdom Mind Active")
    print("=" * 50)
    reading = mind.read_moment("What is the forge's path?")
    print(f"Hexagram: {reading.get('hexagram_number')}: {reading.get('hexagram_english', '')}")
    print(f"Status: {mind.get_status()}")
