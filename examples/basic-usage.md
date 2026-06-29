# Basic Usage Examples

All examples assume you're running from the farewell-agent directory:
```bash
cd C:\Users\You\Documents\farewell-agent
```

## Scenario 1: New Project, First Time

```bash
# 1. Daily readiness
py -m farewell_agent daily

# 2. Register your Flutter project
py -m farewell_agent setup-project C:\Users\You\Documents\my-flutter-app

# 3. Check status
py -m farewell_agent status
# → Farewell: ON | 002-my-flutter-app | BUILD | Skills: 18 | Tim

# 4. Run a task
py -m farewell_agent run "add a login screen with email and password fields"
```

## Scenario 2: Quick Task

```bash
# Already set up, just run
py -m farewell_agent run "fix the date parsing bug in utils/date_helper.dart"
```

## Scenario 3: Research Mode

```bash
# Switch to plan mode for research
py -m farewell_agent workmode plan

# Now try to deploy (will be blocked — plan mode)
py -m farewell_agent run "deploy to production"
# → [FAIL] Task 'deploy' needs build mode — you're in PLAN.
# → Run `farewell-agent workmode build` first.

# Plan mode lets you research safely
py -m farewell_agent workmode build
py -m farewell_agent run "deploy to production"
```

## Scenario 4: Using Memory

```bash
# Save project facts
py -m farewell_agent memory save "Flutter 3.24, Riverpod 2.5, GoRouter 14.0"
py -m farewell_agent memory save "Build command: flutter build windows"

# Save user preferences
py -m farewell_agent memory save --target user "I'm a beginner, explain step by step"

# View memory
py -m farewell_agent memory show
```

## Scenario 5: Multi-Project

```bash
# Register multiple projects
py -m farewell_agent setup-project C:\Users\You\Documents\service-hub
py -m farewell_agent setup-project C:\Users\You\Documents\web-app

# List all projects
py -m farewell_agent project
# → 001 - farewell-assistant (python, PYTHON)
# → 002 - service-hub (flutter, DART) <- active
# → 003 - web-app (nextjs, TYPESCRIPT)

# Switch project
py -m farewell_agent project 003
py -m farewell_agent run "fix the nav bar responsiveness"
```
