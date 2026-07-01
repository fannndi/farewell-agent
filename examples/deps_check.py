import io, sys
from pathlib import Path
from datetime import datetime

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPOS = {
    "9Router": "decolua/9router",
    "ECC": "affaan-m/ECC",
    "awesome-opencode": "awesome-opencode/awesome-opencode",
    "Hermes Agent": "NousResearch/hermes-agent",
    "Hermes Self-Evolution": "NousResearch/hermes-agent-self-evolution",
}

def check_github(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            tag = r.json().get("tag_name", "?")
            return f"OK ({tag})"
        elif r.status_code == 403:
            return "? (rate-limited)"
        else:
            return f"HTTP {r.status_code}"
    except requests.RequestException as e:
        return f"FAIL ({e})"

def main():
    root = Path(__file__).resolve().parent.parent

    print("=" * 54)
    print("  Farewell-Agent -- Dependency Health Check")
    print("=" * 54)
    print()

    print(f"  Project root : {root}")
    print(f"  Python       : {sys.version.split()[0]}")
    print(f"  Platform     : {sys.platform}")
    print(f"  Checked at   : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print()

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        import tomllib
        data = tomllib.loads(text)
        deps = data.get("project", {}).get("dependencies", [])
        print(f"  Dependencies : {', '.join(deps) if deps else 'none'}")
    print()

    print("  -- Local Dirs --")
    for name, _ in REPOS.items():
        d = root / name.lower().replace(" ", "-")
        status = "EXISTS" if d.exists() else "MISSING"
        print(f"    {name:25s}  {status}")

    print()
    print("  -- GitHub Latest Release --")
    for name, repo in REPOS.items():
        status = check_github(repo)
        print(f"    {name:25s}  {status}")

    print()
    print("=" * 54)
    print("  FOOTER")
    print(f"  Project: 001-farewell-agent")
    print(f"  Status: {datetime.now():%Y-%m-%d %H:%M:%S} -- deps check complete")
    print("=" * 54)

if __name__ == "__main__":
    main()
