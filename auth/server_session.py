from __future__ import annotations

import hashlib, hmac, json, os, secrets, sqlite3, time
from pathlib import Path
from typing import Any, Dict

SESSION_MAX_AGE_SECONDS = 12 * 60 * 60

def _secret() -> bytes:
    value = os.getenv("AUTH_SESSION_SECRET", "").strip() or os.getenv("AUTH_COOKIE_SECRET", "").strip()
    if value:
        return value.encode()
    if os.getenv("CAS_ENVIRONMENT", "prod").lower() != "local":
        raise RuntimeError("AUTH_SESSION_SECRET is required outside the local environment.")
    path = Path(__file__).resolve().parents[1] / ".cas_session_secret"
    if not path.exists():
        path.write_text(secrets.token_urlsafe(48) + "\n", encoding="utf-8"); os.chmod(path, 0o600)
    return path.read_text(encoding="utf-8").strip().encode()

class ServerSessionStore:
    def __init__(self) -> None:
        self.path = Path(os.getenv("CAS_SESSION_DB_PATH") or Path(__file__).resolve().parents[1] / ".cas_sessions.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True); self.secret = _secret()
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, payload TEXT NOT NULL, sig TEXT NOT NULL, exp INTEGER NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS handoffs (ticket TEXT PRIMARY KEY, session_id TEXT NOT NULL, exp INTEGER NOT NULL)")
    def _db(self) -> sqlite3.Connection: return sqlite3.connect(self.path)
    def _sign(self, payload: str) -> str: return hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
    def _purge(self, db: sqlite3.Connection, now: int) -> None:
        db.execute("DELETE FROM sessions WHERE exp < ?", (now,)); db.execute("DELETE FROM handoffs WHERE exp < ?", (now,))
    def create(self, user: Dict[str, Any]) -> str:
        now, sid = int(time.time()), secrets.token_urlsafe(32); payload = json.dumps(user, separators=(",", ":"), sort_keys=True)
        with self._db() as db: self._purge(db, now); db.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)", (sid, payload, self._sign(payload), now + SESSION_MAX_AGE_SECONDS))
        return sid
    def issue_ticket(self, sid: str) -> str:
        ticket, now = secrets.token_urlsafe(32), int(time.time())
        with self._db() as db: self._purge(db, now); db.execute("INSERT INTO handoffs VALUES (?, ?, ?)", (hashlib.sha256(ticket.encode()).hexdigest(), sid, now + 60))
        return ticket
    def consume_ticket(self, ticket: str) -> str | None:
        key, now = hashlib.sha256(ticket.encode()).hexdigest(), int(time.time())
        with self._db() as db:
            self._purge(db, now); row = db.execute("SELECT session_id FROM handoffs WHERE ticket=?", (key,)).fetchone(); db.execute("DELETE FROM handoffs WHERE ticket=?", (key,))
        return str(row[0]) if row else None
    def get(self, sid: str) -> Dict[str, Any] | None:
        with self._db() as db: row = db.execute("SELECT payload, sig FROM sessions WHERE id=? AND exp>=?", (sid, int(time.time()))).fetchone()
        if not row or not hmac.compare_digest(row[1], self._sign(row[0])): return None
        try: value = json.loads(row[0])
        except json.JSONDecodeError: return None
        return value if isinstance(value, dict) else None
    def revoke(self, sid: str) -> None:
        with self._db() as db: db.execute("DELETE FROM sessions WHERE id=?", (sid,))

_STORE: ServerSessionStore | None = None
def session_store() -> ServerSessionStore:
    global _STORE
    if _STORE is None: _STORE = ServerSessionStore()
    return _STORE
