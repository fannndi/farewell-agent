#!/usr/bin/env bash
set -euo pipefail

# farewell-agent — Linux/Ubuntu installer
# Usage: curl -fsSL https://raw.githubusercontent.com/.../install.sh | bash

REPO="https://github.com/Fannndi/farewell-agent"
INSTALL_DIR="${INSTALL_DIR:-$HOME/farewell-agent}"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/farewell-agent"
PYTHON="${PYTHON:-python3}"

echo "==> farewell-agent installer (Linux)"
echo "    Install dir: $INSTALL_DIR"
echo "    Data dir:    $DATA_DIR"

# 1. Dependencies
echo "==> Checking dependencies..."
for cmd in git "$PYTHON" pip3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "FAIL: $cmd not found. Install with: sudo apt install -y git python3 python3-pip"
        exit 1
    fi
done

# 2. Clone / update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "==> Updating existing install..."
    git -C "$INSTALL_DIR" pull --ff-only
else
    echo "==> Cloning farewell-agent..."
    git clone "$REPO" "$INSTALL_DIR"
fi

# 3. Python deps
echo "==> Installing Python dependencies..."
pip3 install -q -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || true

# 4. Setup submodules / dependencies
echo "==> Setting up dependencies..."
cd "$INSTALL_DIR"
$PYTHON -m farewell_agent.setup 2>/dev/null || {
    # Manual clone fallback
    for repo in \
        "https://github.com/decolua/9router.git|9router|master" \
        "https://github.com/anomalyco/opencode.git|opencode|main" \
        "https://github.com/anomalyco/awesome-opencode.git|awesome-opencode|main"; do
        url="${repo%%|*}"; name="${repo#*|}"; name="${name%|*}"; branch="${repo##*|}"
        if [ ! -d "$name/.git" ]; then
            echo "  Cloning $name..."
            git clone --branch "$branch" "$url" "$name" 2>/dev/null || echo "  SKIP $name"
        fi
    done
}

# 5. Create data dirs
mkdir -p "$DATA_DIR"/{memory,context,manifests,skills}

# 6. Symlink from install dir into data dir
ln -sf "$INSTALL_DIR/.farewell/roles.json" "$DATA_DIR/roles.json" 2>/dev/null || true

# 7. 9Router service (optional)
if command -v systemctl &>/dev/null; then
    echo "==> Installing 9Router systemd service..."
    cat >/tmp/9router.service <<'SERVICE'
[Unit]
Description=9Router LLM Proxy
After=network.target

[Service]
Type=simple
ExecStart=npx 9router
WorkingDirectory=%h
Restart=on-failure
RestartSec=5
Environment=PORT=20128
Environment=NODE_ENV=production

[Install]
WantedBy=default.target
SERVICE
    sudo mv /tmp/9router.service /etc/systemd/user/9router.service 2>/dev/null || {
        mkdir -p "$HOME/.config/systemd/user"
        mv /tmp/9router.service "$HOME/.config/systemd/user/9router.service"
        systemctl --user daemon-reload
        echo "  Enable: systemctl --user enable --now 9router"
    }
fi

# 8. Shell alias
SHELL_RC="$HOME/.bashrc"
if [ -n "${ZSH_VERSION:-}" ]; then SHELL_RC="$HOME/.zshrc"; fi
if ! grep -q "farewell-agent" "$SHELL_RC" 2>/dev/null; then
    echo "==> Adding alias to $SHELL_RC"
    cat >> "$SHELL_RC" <<ALIAS
alias farewell-agent='$PYTHON -m farewell_agent'
alias fa='$PYTHON -m farewell_agent'
ALIAS
fi

echo ""
echo "========================================"
echo "  farewell-agent installed!"
echo "  Run: farewell-agent daily"
echo "  Or:  fa run <task>"
echo "========================================"
