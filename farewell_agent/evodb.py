"""Evolution database -- SQLite-backed performance tracking."""

import sqlite3, json
from datetime import datetime, timezone
from pathlib import Path
from . import config

DB_NAME = "evodb.sqlite"

def _db_path() -> Path:
    return config.FAREWELL_DIR / DB_NAME

def _conn():
    return sqlite3.connect(str(_db_path()))

def init():
    db = _db_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            task_class TEXT,
            agent TEXT NOT NULL,
            model TEXT NOT NULL,
            raw_input TEXT,
            enriched_input TEXT,
            footer_ok INTEGER DEFAULT 0,
            duration_s REAL,
            tokens_in INTEGER DEFAULT 0,
            tokens_out INTEGER DEFAULT 0,
            cost REAL DEFAULT 0,
            success INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project);
        CREATE INDEX IF NOT EXISTS idx_tasks_model ON tasks(model);
        CREATE INDEX IF NOT EXISTS idx_tasks_class ON tasks(task_class);
        CREATE TABLE IF NOT EXISTS evolutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            applied_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def insert_task(project: str, task_class: str | None, agent: str, model: str,
                raw_input: str = "", enriched_input: str = "", footer_ok: bool = False,
                duration_s: float = 0, success: bool = False):
    conn = _conn()
    conn.execute("""
        INSERT INTO tasks (project, task_class, agent, model, raw_input, enriched_input,
                          footer_ok, duration_s, success, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project, task_class, agent, model, raw_input[:500], enriched_input[:500],
          int(footer_ok), duration_s, int(success), datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

def model_performance(project: str | None = None) -> list[dict]:
    conn = _conn()
    where = "WHERE project = ?" if project else ""
    params = (project,) if project else ()
    rows = conn.execute(f"""
        SELECT model, task_class,
               COUNT(*) as total,
               SUM(success) as successes,
               SUM(footer_ok) as footers,
               ROUND(AVG(duration_s), 1) as avg_duration
        FROM tasks {where}
        GROUP BY model, task_class
        ORDER BY total DESC
    """, params).fetchall()
    conn.close()
    return [
        {"model": r[0], "task_class": r[1], "total": r[2],
         "successes": r[3], "footers": r[4], "avg_duration": r[5]}
        for r in rows
    ]

def best_model_per_task_class(project: str | None = None, min_tasks: int = 3) -> dict:
    perf = model_performance(project)
    best = {}
    for p in perf:
        if p["total"] < min_tasks: continue
        cls = p["task_class"] or "default"
        rate = p["successes"] / p["total"] if p["total"] > 0 else 0
        if cls not in best or rate > best[cls]["rate"]:
            best[cls] = {"model": p["model"], "rate": rate, "total": p["total"],
                         "avg_duration": p["avg_duration"]}
    return best

def footer_rate(project: str | None = None) -> float:
    conn = _conn()
    where = "WHERE project = ?" if project else ""
    params = (project,) if project else ()
    row = conn.execute(f"SELECT COUNT(*), SUM(footer_ok) FROM tasks {where}", params).fetchone()
    conn.close()
    total, ok = row[0] or 0, row[1] or 0
    return ok / total if total else 1.0

def record_evolution(metric: str, old_value: str, new_value: str):
    conn = _conn()
    conn.execute("INSERT INTO evolutions (metric, old_value, new_value, applied_at) VALUES (?, ?, ?, ?)",
                 (metric, str(old_value), str(new_value), datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

def recent_evolutions(limit: int = 10) -> list[dict]:
    conn = _conn()
    rows = conn.execute("SELECT metric, old_value, new_value, applied_at FROM evolutions ORDER BY id DESC LIMIT ?",
                        (limit,)).fetchall()
    conn.close()
    return [{"metric": r[0], "old_value": r[1], "new_value": r[2], "applied_at": r[3]} for r in rows]
