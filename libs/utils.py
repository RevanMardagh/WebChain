import subprocess

def run_command(cmd: list, dry_run: bool = False):
    """
    Executes a shell command.
    If dry_run=True, prints the command and returns an empty string.
    """
    cmd_str = " ".join(cmd)

    if dry_run:
        print(f"[DRY-RUN] Would execute: {cmd_str}")
        return ""

    print(f"[INFO] Executing: {cmd_str}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd_str}")
        print(e.stderr)
        return ""
