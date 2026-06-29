import json
from . import config
from .state.io import read_json, write_json

STACK_SKILLS = {
    "python": ["python-patterns", "python-testing", "fastapi-patterns", "django-patterns", "django-security", "backend-patterns"],
    "flutter": ["dart-flutter-patterns", "compose-multiplatform-patterns", "flutter-dart-code-review"],
    "dart": ["dart-flutter-patterns", "flutter-dart-code-review"],
    "react": ["react-patterns", "react-testing", "react-performance", "frontend-patterns"],
    "nextjs": ["react-patterns", "react-testing", "nextjs-turbopack", "frontend-patterns"],
    "vue": ["vue-patterns", "ui-to-vue"],
    "nodejs": ["nestjs-patterns", "prisma-patterns", "backend-patterns", "database-migrations"],
    "golang": ["golang-patterns", "golang-testing"],
    "rust": ["rust-patterns", "rust-testing"],
    "kotlin": ["kotlin-patterns", "kotlin-coroutines-flows", "kotlin-testing"],
    "swift": ["swiftui-patterns", "swift-concurrency-6-2", "swift-actor-persistence"],
    "database": ["postgres-patterns", "mysql-patterns", "database-migrations", "redis-patterns"],
    "docker": ["docker-patterns", "deployment-patterns"],
    "infra": ["kubernetes-patterns", "deployment-patterns", "docker-patterns"],
}

COMMON_SKILLS = ["git-workflow", "tdd-workflow", "coding-standards", "error-handling",
                 "security-review", "verification-loop", "agent-self-evaluation", "accessibility"]

def find_matching(stack: list[str]) -> list[str]:
    matched = set()
    for s in stack:
        sl = s.lower()
        for keyword, skills in STACK_SKILLS.items():
            if keyword in sl or sl in keyword or sl.startswith(keyword):
                matched.update(skills)
    matched.update(COMMON_SKILLS)
    return sorted(matched)

def get_skills(code: str, name: str) -> list[str]:
    mf = config.MANIFESTS_DIR / f"{code}-{name}.json"
    if mf.exists():
        data = read_json(mf)
        if data: return data.get("skills", [])
    return []

def write_active_skills(code: str, name: str):
    skills = get_skills(code, name)
    if not skills:
        mf = config.MANIFESTS_DIR / f"{code}-{name}.json"
        stack = []
        if mf.exists():
            data = read_json(mf)
            if data: stack = data.get("stack", [])
        if not stack: stack = [code.split("-")[0] if "-" in code else code]
        skills = find_matching(stack) + COMMON_SKILLS
        skills = sorted(set(skills))
    paths = [f"ecc/skills/{s}/SKILL.md" for s in skills if (config.ECC_DIR / "skills" / s / "SKILL.md").exists()]
    paths += [".farewell/custom-skills"]
    manifest = {"paths": paths, "project": f"{code}-{name}", "total": len(paths)}
    mf = config.STATE_DIR / "active-skills.json"
    write_json(mf, manifest)
