#app/context_store.py
from collections import defaultdict

# maps session_id → list of (role, text)
CONTEXT_STORE = defaultdict(list)