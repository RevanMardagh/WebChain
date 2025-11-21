# utils/runner.py
import subprocess
from typing import List

def run_command(cmd: List[str], dry_run: bool = False) -> str:
    """
    Executes a shell command.
    If dry_run=True, prints the command and returns empty string.
    """
    cmd_str = " ".join(cmd)

    if dry_run:
        print(f"[DRY-RUN] Would execute: {cmd_str}")
        return ""

    print(f"[RUN] Executing: {cmd_str}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd_str}")
        if e.stderr:
            print(f"       {e.stderr.strip()}")
        return ""
    except FileNotFoundError:
        tool = cmd[0]
        print(f"[ERROR] Tool not found: {tool} is not installed or not in PATH")
        return ""