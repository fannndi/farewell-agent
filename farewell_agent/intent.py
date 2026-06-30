"""Intent classifier -- task description -> workflow/agent mapping."""

# High-level workflow keywords (Indonesian + English)
WORKFLOW_RULES = {
    "audit": [
        "audit", "review project", "cek project", "periksa project",
        "code review", "kualitas kode", "code quality",
    ],
    "feature": [
        "tambah fitur", "fitur baru", "new feature", "add feature",
        "bikin fitur", "buat fitur",
    ],
    "fix": [
        "perbaiki", "bug", "error", "fix bug", "problem",
        "ga jalan", "rusak", "broken", "not working",
    ],
    "learn": [
        "belajar", "learn", "riset", "research", "pelajari",
        "cari tahu", "dokumentasi", "documentation",
    ],
    "health": [
        "cek kesehatan", "health check", "cek system", "cek 9router",
        "daily check", "readiness", "cek semua",
    ],
    "refactor": [
        "refactor", "rapihin", "rapikan", "bersihin", "clean up",
        "dead code", "bersihkan",
    ],
}

# Task-level keywords (map to specific OpenCode agents)
TASK_RULES = {
    "security-review": [
        "security", "auth", "vulnerability", "password", "encryption",
        "xss", "sqli", "csrf", "injection",
    ],
    "verification-loop": [
        "test", "verify", "qa", "unit test", "integration test",
        "coverage", "assert", "testing",
    ],
    "self-heal": [
        "build error", "compile error", "fix build", "gagal compile",
        "error build", "broken build", "syntax error",
    ],
    "deploy": [
        "deploy", "release", "publish", "ci/cd", "pipeline",
        "production", "staging", "rollback",
    ],
    "rust-debug": [
        "rust", "cargo", "lifetime", "borrow checker",
    ],
    "kotlin-debug": [
        "kotlin", "kotlin build", "gradle build", "android build",
    ],
}


def classify_workflow(task: str) -> str | None:
    """Detect high-level workflow from task description."""
    t = task.lower()
    for wf, keywords in WORKFLOW_RULES.items():
        for kw in keywords:
            if kw in t:
                return wf
    return None


def classify_task(task: str) -> str | None:
    """Detect specific task type."""
    t = task.lower()
    for cls, keywords in TASK_RULES.items():
        for kw in keywords:
            if kw in t:
                return cls
    return None


def classify(task: str) -> tuple[str | None, str | None]:
    """Returns (workflow, task_class). Both can be None."""
    return classify_workflow(task), classify_task(task)


# ── Natural language classifier for REPL ──

NATURAL_INTENTS = {
    "daily": [
        "cek kesehatan", "health check", "daily", "readiness",
        "cek 9router", "cek system", "cek semua",
    ],
    "setup_project": [
        "daftarin project", "setup project", "daftar project",
        "register project", "project baru",
    ],
    "start_project": [
        "mulai project", "start project", "buat project baru",
        "bikin project",
    ],
    "evolution": [
        "update tools", "upgrade tools", "evolution", "evolusi",
        "pull repo", "update semua",
    ],
    "exit": [
        "exit", "quit", "keluar", "bye", "selesai", "sampe jumpa",
    ],
    "help": [
        "/help", "help", "bantuan", "cara pakai", "?",
    ],
}

SHORTCUT_MAP = {
    "/daily": "daily",
    "/d": "daily",
    "/evolution": "evolution",
    "/ev": "evolution",
    "/setup-project": "setup_project",
    "/start-project": "start_project",
    "/help": "help",
    "/h": "help",
    "/exit": "exit",
    "/keluar": "exit",
    "/q": "exit",
}


def classify_natural(text: str) -> dict:
    """Natural language -> {intent, task, workflow, path}."""
    t = text.strip().lower()

    # Shortcut commands
    if t.split()[0] in SHORTCUT_MAP if " " in t else t in SHORTCUT_MAP:
        cmd = t.split()[0] if " " in t else t
        intent = SHORTCUT_MAP[cmd]
        rest = text[len(cmd):].strip() if " " in text else ""
        return {"intent": intent, "task": rest}

    # Detect intent by content
    for intent, keywords in NATURAL_INTENTS.items():
        if any(kw in t for kw in keywords):
            if intent == "setup_project":
                path = _extract_path(text)
                return {"intent": intent, "task": text, "path": path}
            return {"intent": intent, "task": text}

    # Default: run task via dispatch
    wf = classify_workflow(text)
    return {"intent": "run", "task": text, "workflow": wf}


def _extract_path(text: str) -> str:
    """Extract a filesystem path from natural language."""
    import re
    # Match paths like C:\... or /home/... or just words after "di"
    patterns = [
        r'(?<=di\s)[A-Za-z]:\\[^\s]*',   # "di C:\path"
        r'(?<=di\s)/[^\s]*',               # "di /home/user/path"
        r'(?<=path\s)[A-Za-z]:\\[^\s]*',  # "path C:\..."
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group().strip()
    return ""
