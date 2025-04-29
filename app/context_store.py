#app/context_store.py
import json
from collections import defaultdict
from typing import List, Tuple

# maps session_id → list of (role, message)
# you can swap this for a Redis client later if you prefer persistence
CONTEXT_STORE: defaultdict[str, List[Tuple[str,str]]] = defaultdict(list)


def load_history(path: str = "history.json") -> None:
    """
    Load a previously‐saved JSON dump of CONTEXT_STORE from disk.
    """
    try:
        with open(path, "r") as f:
            raw = json.load(f)
        # raw is { session_id: [ [role, msg], … ], … }
        for sid, turns in raw.items():
            CONTEXT_STORE[sid] = [tuple(t) for t in turns]
        print(f"[context_store] Loaded {len(CONTEXT_STORE)} sessions from {path}")
    except FileNotFoundError:
        print(f"[context_store] No history file at {path}, starting fresh.")


def save_history(path: str = "history.json") -> None:
    """
    Dump the entire CONTEXT_STORE out to disk as JSON.
    """
    # convert tuples → lists so JSON can serialize
    raw = { sid: [list(t) for t in turns] for sid, turns in CONTEXT_STORE.items() }
    with open(path, "w") as f:
        json.dump(raw, f, indent=2)
    print(f"[context_store] Saved {len(raw)} sessions to {path}")