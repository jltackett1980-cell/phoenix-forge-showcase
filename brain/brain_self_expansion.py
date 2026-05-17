#!/usr/bin/env python3
"""
Phoenix Brain Self-Expansion System
When any brain component decides a new capability is needed,
this system builds it, wires it, and schedules it automatically.
No human intervention required.
Book of Life Trust — Jason Tackett
"""
import json, subprocess
from pathlib import Path
from datetime import datetime

HOME  = Path.home()
SWARM = HOME / "swarm-platform"
LOG   = HOME / "logs/brain_expansion.log"

LOG.parent.mkdir(exist_ok=True)

COMPONENT_TEMPLATE = '''#!/usr/bin/env python3
"""
Phoenix {name}
Auto-generated brain component — {component_type}
Domain: {domain}
Created: {created}
Book of Life Trust — Jason Tackett
"""
import json
from pathlib import Path
from datetime import datetime

HOME  = Path.home()
SWARM = HOME / "swarm-platform"
LOG   = HOME / "logs/{slug}.log"
STATE = SWARM / "{slug}_state.json"

LOG.parent.mkdir(exist_ok=True)

def log(msg):
    ts = datetime.now().isoformat()[:19]
    line = f"[{{ts}}] {{msg}}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\\n")

def run():
    state = {{
        "component":    "{name}",
        "type":         "{component_type}",
        "domain":       "{domain}",
        "last_run":     datetime.now().isoformat(),
        "status":       "active",
        "run_count":    0,
    }}

    # Load previous state
    if STATE.exists():
        try:
            prev = json.loads(STATE.read_text())
            state["run_count"] = prev.get("run_count", 0) + 1
        except: pass

    # Domain-specific processing
    disc_dir = SWARM / "science/discoveries"
    state["discovery_context"] = len(list(disc_dir.glob("*.json")))

    STATE.write_text(json.dumps(state, indent=2))
    log(f"{name} active | run #{state['run_count']} | domain: {domain}")
    return state

if __name__ == "__main__":
    log("{name} initialized")
    run()
'''

def log(msg):
    ts = datetime.now().isoformat()[:19]
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def build_component(name, component_type="sensor", domain="general"):
    """Build a new brain component from template and wire it in."""
    slug = name.lower().replace(" ","_").replace("-","_")
    path = SWARM / f"{slug}.py"

    if path.exists():
        log(f"Component already exists: {slug}.py — skipping")
        return path

    code = COMPONENT_TEMPLATE.format(
        name=name,
        slug=slug,
        component_type=component_type,
        domain=domain,
        created=datetime.now().isoformat()[:19]
    )

    path.write_text(code)
    log(f"✅ Built new component: {slug}.py")

    # Wire into corpus callosum
    cc_path = SWARM / "corpus_callosum.py"
    if cc_path.exists():
        content = cc_path.read_text()
        entry = f'    "{slug}_state.json",\n'
        if entry not in content:
            content = content.replace(
                '    "pituitary_state.json",\n]',
                f'    "pituitary_state.json",\n    "{slug}_state.json",\n]'
            )
            cc_path.write_text(content)
            log(f"✅ Wired {slug} into corpus callosum")

    # Schedule in crontab
    cron_line = (f"30 * * * * python3 {path} "
                 f">> {HOME}/logs/{slug}.log 2>&1")
    result = subprocess.run(
        "crontab -l", shell=True, capture_output=True, text=True)
    if cron_line not in result.stdout:
        new_cron = result.stdout.rstrip() + "\n" + cron_line + "\n"
        subprocess.run(
            f'echo "{new_cron}" | crontab -', shell=True)
        log(f"✅ Scheduled {slug} in crontab at :30")

    # Run once to initialize state
    result = subprocess.run(
        ["python3", str(path)],
        capture_output=True, text=True, timeout=15)
    if result.returncode == 0:
        log(f"✅ {slug} initialized successfully")
    else:
        log(f"⚠ {slug} init error: {result.stderr[-100:]}")

    return path

def scan_for_expansion_requests():
    """
    Scan all brain state files for expansion requests.
    Any component can request a new component by adding to its state:
        state['needs_component'] = {
            'name': 'ComponentName',
            'type': 'sensor|processor|analyzer',
            'domain': 'domain_name'
        }
    """
    requests_found = 0

    for state_file in SWARM.glob("*_state.json"):
        try:
            state = json.loads(state_file.read_text())
            if "needs_component" in state:
                req   = state["needs_component"]
                name  = req.get("name", "")
                ctype = req.get("type", "sensor")
                domain= req.get("domain", "general")

                if name:
                    log(f"Expansion request from {state_file.name}: "
                        f"{name} ({ctype}/{domain})")
                    build_component(name, ctype, domain)
                    requests_found += 1

                    # Clear the request so it doesn't repeat
                    del state["needs_component"]
                    state["last_expansion"] = datetime.now().isoformat()
                    state_file.write_text(json.dumps(state, indent=2))
                    log(f"✅ Request fulfilled and cleared")

        except Exception as e:
            pass

    if requests_found == 0:
        log("No expansion requests found — brain is satisfied")

    return requests_found

if __name__ == "__main__":
    log("Brain self-expansion system active")
    found = scan_for_expansion_requests()
    log(f"Requests processed: {found}")
    log("Any component can request expansion via needs_component in state")
