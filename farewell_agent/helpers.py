import json, os, platform, sys

_COLORS = {
    "green": "\033[92m", "yellow": "\033[93m", "red": "\033[91m",
    "cyan": "\033[96m", "gray": "\033[90m", "magenta": "\033[95m",
    "blue": "\033[94m", "white": "\033[97m", "reset": "\033[0m",
}

def _use_color():
    if os.environ.get("NO_COLOR"): return False
    if platform.system() == "Windows":
        return bool(os.environ.get("WT_SESSION") or os.environ.get("ConEmuANSI")
                    or os.environ.get("ANSICON") or os.environ.get("VSCODE_PID"))
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_USE_COLOR = _use_color()

def c(text: str, color: str) -> str:
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}" if _USE_COLOR else text

def step(step: str, msg: str): print(f"\n{c(f'[{step}] {msg}', 'cyan')}")
def ok(msg: str): print(f"  {c('[OK]', 'green')} {msg}")
def skip(msg: str): print(f"  {c('[SKIP]', 'yellow')} {msg}")
def fail(msg: str): print(f"  {c('[FAIL]', 'red')} {msg}")
def info(msg: str): print(f"  {c('[..]', 'gray')} {msg}")
