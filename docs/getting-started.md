# Getting Started

## Prerequisites

- Python 3.10+
- OpenCode (`opencode run` — install from [opencode.ai](https://opencode.ai))
- 9Router (Node.js, port 20128)
- Git (for ECC/awesome-opencode sync)

## Installation

```bash
# Clone repo
git clone https://github.com/fannndi/farewell-agent.git
cd farewell-agent

# Install Python dependencies
pip install pyyaml
```

## Quick Start — First Time

### 0. Clone dependencies

```bash
py -m farewell_agent setup
```
Ini clone 3 repo penting: **9Router** (LLM proxy), **ECC** (271 skills), **awesome-opencode** (plugin registry).

### 1. Prepare config

Copy the example API key file and fill in your model keys:

```bash
cp .api-key.example.txt api-key.txt
# Edit api-key.txt with your actual model names
```

Example `api-key.txt`:
```
NINEROUTER_API_KEY=sk-your-key
LEADER_1=ocg/deepseek-v4-flash
SPECIAL=oc/deepseek-v4-flash-free
WORKER=oc/mimo-v2.5-free
WORKER_PRO=ocg/deepseek-v4-flash
```

### 2. Run your first daily

```bash
py -m farewell_agent daily
```

This starts 9Router, syncs ECC skills, regenerates config, and shows system readiness.

### 3. Register your project

```bash
# Go to your project first, then:
cd /path/to/your-project
py -m C:\path\to\farewell-agent -m farewell_agent start-project
```

Or with explicit path:
```bash
cd C:\Users\You\Documents\farewell-agent
py -m farewell_agent setup-project C:\Users\You\Documents\my-project
```

### 4. Check status

```bash
py -m farewell_agent status
```

### 5. Run a task

```bash
py -m farewell_agent run "Add error handling to the API routes"
```

## Daily workflow

Once you're set up, your daily routine is just:

```bash
py -m farewell_agent daily
py -m farewell_agent run "continue working on [task]"
```

No need to remember project codes, team tiers, or model names — the agent resolves everything automatically.

## Switch team tier

```bash
py -m farewell_agent team divisi   # Premium models for all tasks
py -m farewell_agent team tim      # Default — balanced
py -m farewell_agent team bawahan  # Most economical
```

## Switch work mode

```bash
py -m farewell_agent workmode plan   # Read-only (research/planning)
py -m farewell_agent workmode build  # Full access (execution)
```
