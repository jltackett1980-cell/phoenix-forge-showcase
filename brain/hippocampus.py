#!/usr/bin/env python3
"""
HIPPOCAMPUS — Memory Consolidation
Stores discoveries and learns patterns from evolution
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from collections import deque

HOME = Path.home()
SWARM = HOME / "swarm-platform"
LOG = HOME / "logs/hippocampus.log"
STATE = SWARM / "hippocampus_state.json"
MEMORY = SWARM / "hippocampus_memory.json"

logging.basicConfig(filename=LOG, level=logging.INFO, format='%(asctime)s [HIPPOCAMPUS] %(message)s')

class Hippocampus:
    def __init__(self):
        self.memories = deque(maxlen=2000)
        self.patterns = {}
        self.discovery_count = 0
        self.load_state()
    
    def load_state(self):
        if MEMORY.exists():
            try:
                with open(MEMORY) as f:
                    data = json.load(f)
                    self.memories = deque(data, maxlen=2000)
            except:
                pass
        if STATE.exists():
            try:
                with open(STATE) as f:
                    data = json.load(f)
                    self.patterns = data.get("patterns", {})
                    self.discovery_count = data.get("discovery_count", 0)
            except:
                pass
    
    def save_state(self):
        with open(STATE, "w") as f:
            json.dump({
                "patterns": self.patterns,
                "discovery_count": self.discovery_count,
                "last_update": datetime.now().isoformat()
            }, f, indent=2)
        with open(MEMORY, "w") as f:
            json.dump(list(self.memories), f, indent=2)
    
    def store_discovery(self, discovery_type, content, importance=1):
        """Store a discovery from meta-evolver"""
        memory = {
            "type": discovery_type,
            "content": content[:500],
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "id": self.discovery_count
        }
        self.memories.append(memory)
        self.discovery_count += 1
        self.save_state()
        logging.info(f"Stored {discovery_type}: {content[:50]}...")
        
        # Learn pattern
        pattern_key = f"{discovery_type}_pattern"
        if pattern_key not in self.patterns:
            self.patterns[pattern_key] = 0
        self.patterns[pattern_key] += 1
        
        return self.discovery_count
    
    def recall_recent(self, limit=10):
        """Recall recent discoveries"""
        return list(self.memories)[-limit:]
    
    def get_status(self):
        return {
            "discovery_count": self.discovery_count,
            "memory_count": len(self.memories),
            "pattern_count": len(self.patterns),
            "patterns": self.patterns
        }

if __name__ == "__main__":
    h = Hippocampus()
    print(json.dumps(h.get_status(), indent=2))

    def observe(self, **kw):
        return self.remember() if hasattr(self, 'remember') else {}

Hippocampus.observe = lambda self, **kw: {}
