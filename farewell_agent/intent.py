TASK_RULES = {
    "security-review": [
        "security", "auth", "vulnerability", "password", "encryption",
        "xss", "sqli", "csrf", "injection", "audit security",
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
        "rust", "cargo", "lifetime", "borrow checker", "unsafe rust",
    ],
    "kotlin-debug": [
        "kotlin", "kotlin build", "gradle build", "android build",
    ],
}

def classify(task: str) -> str | None:
    task_lower = task.lower()
    for cls, keywords in TASK_RULES.items():
        for kw in keywords:
            if kw in task_lower:
                return cls
    return None
