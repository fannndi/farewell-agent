# Command Reference

```
farewell-agent

Usage:
  farewell-agent workmode [plan|build|status]
  farewell-agent team [divisi|tim|bawahan|status]
  farewell-agent status
  farewell-agent daily
  farewell-agent project [list|switch <code>]
  farewell-agent setup-project <path>
  farewell-agent start-project [<path>]
  farewell-agent org [chart|roles|workflow|priority|all]
  farewell-agent cool [list|search <q>|info <name>|recommend|stats]
  farewell-agent run "<task description>"
  farewell-agent memory [show|edit|save]
  farewell-agent cost [status]
```

## Core Commands

### `daily`
One command to start 9Router, sync upstream (ECC, awesome-opencode, 9Router), regenerate OpenCode config, and show readiness report.

```
py -m farewell_agent daily
```

### `run`
Single entry point for task execution. Classifies intent, resolves models, calls OpenCode.

```
py -m farewell_agent run "add authentication middleware"
py -m farewell_agent run "audit security vulnerabilities in the login endpoint"
py -m farewell_agent run "fix the failing test suite"
```

### `setup-project`
Register a project by path. Detects stack, creates `.farewell/` symlinks inside the project.

```
py -m farewell_agent setup-project C:\Users\You\Documents\my-project
```

### `start-project`
Auto-detect current directory, show detection, confirm, and register.

```
cd C:\Users\You\Documents\my-project
py -m C:\path\to\farewell-agent -m farewell_agent start-project
```

### `team`
Switch between 3 tiers. Each defines which model serves as LEADER/SPECIAL/WORKER.

```
py -m farewell_agent team divisi     # Premium: LEADER model for everything
py -m farewell_agent team tim        # Default: SPECIAL model (balanced)
py -m farewell_agent team bawahan    # Most economical: WORKER model for all
```

### `workmode`
Switch between read-only (PLAN) and full-access (BUILD).

```
py -m farewell_agent workmode plan   # Research and planning only
py -m farewell_agent workmode build  # Full execution
```

### `memory`
View or edit per-project memory (like Hermes Agent's MEMORY.md).

```
py -m farewell_agent memory show
py -m farewell_agent memory edit                    # Opens in $EDITOR
py -m farewell_agent memory save "Project uses Riverpod for state management"
py -m farewell_agent memory save --target user "User prefers concise answers"
```

### `cost`
View token usage and budget.

```
py -m farewell_agent cost status
```

### `status`
One-line summary: project, mode, team, skill count, budget.

```
py -m farewell_agent status
```

## Info Commands

### `org`
Display organization hierarchy. Models resolve live from config.

```
py -m farewell_agent org        # shows all
py -m farewell_agent org chart
py -m farewell_agent org roles
py -m farewell_agent org workflow
py -m farewell_agent org priority
```

### `cool`
Browse the awesome-opencode registry.

```
py -m farewell_agent cool stats
py -m farewell_agent cool list
py -m farewell_agent cool search "flutter"
py -m farewell_agent cool info "universal-llm-api-proxy"
py -m farewell_agent cool recommend
```
