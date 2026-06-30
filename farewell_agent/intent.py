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
