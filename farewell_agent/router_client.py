import json, os, socket, sqlite3, urllib.request
from datetime import datetime
from pathlib import Path
from typing import Protocol

class UsageRecord:
    def __init__(self, timestamp: str, model: str, tokens_in: int, tokens_out: int, cost: float):
        self.timestamp = timestamp
        self.model = model
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.cost = cost

class ModelProvider(Protocol):
    def health_check(self) -> bool: ...
    def resolve_model(self, role_key: str) -> str: ...
    def list_combos(self) -> list[dict]: ...
    def usage_since(self, ts: datetime) -> list[UsageRecord]: ...

class NineRouterProvider:
    def __init__(self, host: str = "127.0.0.1", port: int = 20128):
        self.host = host
        self.port = port

    def health_check(self) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            result = sock.connect_ex((self.host, self.port))
            return result == 0
        finally:
            sock.close()

    def resolve_model(self, role_key: str) -> str:
        cfg = self._load_config()
        combos = self._load_combo_names()
        val = cfg.get(role_key, role_key.lower())
        return role_key if role_key in combos else val

    def list_combos(self) -> list[dict]:
        db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
        if not db.exists(): return []
        try:
            conn = sqlite3.connect(str(db))
            cur = conn.execute("SELECT name, kind, models FROM combos")
            combos = []
            for row in cur:
                try: models = json.loads(row[2]) if row[2] else []
                except: models = []
                combos.append({"name": row[0], "kind": row[1], "models": models})
            conn.close()
            return combos
        except: return []

    def usage_since(self, ts: datetime) -> list[UsageRecord]:
        return []

    def _load_config(self) -> dict:
        from . import config
        models = {}
        f = config.ROOT_DIR / "api-key.txt"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if "=" not in line or line.startswith("#"): continue
                k, v = line.split("=", 1)
                models[k.strip()] = v.strip()
        return models

    def _load_combo_names(self) -> set[str]:
        db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
        if not db.exists(): return set()
        try:
            conn = sqlite3.connect(str(db))
            names = {row[0] for row in conn.execute("SELECT name FROM combos")}
            conn.close()
            return names
        except: return set()
