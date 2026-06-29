# Project Setup

## How a project gets registered

When you run `setup-project` or `start-project`, farewall-agent:

1. **Scans your project** — checks for signature files (pyproject.toml, pubspec.yaml, Cargo.toml, etc.)
2. **Detects stack** — identifies frameworks (Flutter, React, Django, etc.)
3. **Registers** in `.farewell/registry.json` with a 3-digit code (001, 002, ...)
4. **Writes skill manifest** — matches your stack against ECC's 271 skills → filtered subset
5. **Injects `.farewell/` symlinks** into your project directory

## What gets injected

After setup, your project will have:

```
your-project/
└── .farewell/
    ├── skills/          → symlink to central ECC skills directory
    ├── AGENTS.md        → symlink to central ECC AGENTS.md
    ├── instructions/    → symlink to farewell-agent instructions/
    ├── memory/          → per-project memory storage
    └── context/         → per-project context files
```

This means your project becomes **self-aware** — OpenCode running from your project can directly access skills, instructions, and memory.

## Example

```bash
# Register a Flutter project
cd C:\Users\You\Documents\farewell-agent
py -m farewell_agent setup-project C:\Users\You\Documents\service-hub

# Output:
# [REGISTERED] 002-service-hub
# Type: flutter | Dominan: DART
# Stack: flutter, dart, nodejs
# Skills: 18 matched
# Symlinks: .farewell/ injected in project
```

## Auto-start projects

The `start-project` command is even simpler — it detects the current directory:

```bash
cd C:\Users\You\Documents\my-flutter-app
py -m C:\path\to\farewell-agent -m farewell_agent start-project

# Output:
# Scanning: C:\Users\You\Documents\my-flutter-app
# Detected: flutter (DART), stack=['flutter', 'dart']
# Register project 'my-flutter-app' as flutter (DART)? [Y/n]
# y
# [OK] 003-my-flutter-app siap
# Skills: 15 matched
# Symlinks injected in project/.farewell/
```

## Switching projects

After registering multiple projects, switch between them:

```bash
py -m farewell_agent project               # list all
py -m farewell_agent project switch 002    # switch to project 002
py -m farewell_agent project 002           # shortcut (same as above)
```
