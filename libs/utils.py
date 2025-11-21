# utils.py
import subprocess
import shutil
from typing import List, Optional

# ANSI color codes
class Colors:
    HEADER = "\033[96m"   # cyan
    OK = "\033[92m"       # green
    WARN = "\033[93m"     # yellow
    ERROR = "\033[91m"    # red
    INFO = "\033[94m"     # blue
    MUTED = "\033[90m"    # gray
    RESET = "\033[0m"

def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"

def run_command(cmd: List[str], dry_run: bool = False) -> str:
    """
    Execute a command and return its stdout as string.
    If dry_run=True, only pretty-print the command and return empty string.
    """
    cmd_str = " ".join(cmd)
    if dry_run:
        print(colorize(f"[DRY-RUN] Would execute: {cmd_str}", Colors.MUTED))
        return ""

    print(colorize(f"[INFO] Executing: {cmd_str}", Colors.INFO))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        # If a tool writes to stderr, include it in output for visibility
        stderr = e.stderr or ""
        print(colorize(f"[ERROR] Command failed: {cmd_str}", Colors.ERROR))
        if stderr.strip():
            print(colorize(stderr.strip(), Colors.ERROR))
        return ""
    except FileNotFoundError:
        print(colorize(f"[ERROR] Command not found: {cmd[0]}", Colors.ERROR))
        return ""

def command_exists(name: str) -> bool:
    """Return True if executable `name` exists in PATH."""
    return shutil.which(name) is not None
