# check_versions.py
import subprocess
import re
from utils import Colors, colorize

def run_pdtm() -> str:
    """Runs the pdtm command and returns raw output."""
    try:
        result = subprocess.run(
            ["pdtm"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return result.stdout
    except FileNotFoundError:
        return None

def parse_pdtm_output(output: str):
    # regex to remove ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    tools = {}

    clean_output = ansi_escape.sub("", output)
    clean_output = clean_output.replace("\r\n", "\n").replace("\r", "\n")

    lines = [line for line in clean_output.splitlines() if re.match(r"^\s*\d+\.", line)]
    trimmed_output = "\n".join(lines)

    pattern = re.compile(
        r"^\s*\d+\.\s+([a-zA-Z0-9\-_]+)\s+"           
        r"\((latest|outdated|not installed|not supported)\)"  
        r"(?:\s+\(([\d\.]+)\))?"                       
        r"(?:\s+➡\s+\(([\d\.]+)\))?",
        re.MULTILINE
    )

    for m in pattern.finditer(trimmed_output):
        name = m.group(1)
        status = m.group(2)
        current = m.group(3) if m.group(3) else None
        latest = m.group(4) if m.group(4) else None

        tools[name] = {
            "status": status,
            "current_version": current,
            "latest_version": latest,
        }

    return tools

# Only show these tools
CORE_TOOLS = {"subfinder", "dnsx", "naabu", "httpx", "katana"}

def check_projectdiscovery_tools():
    output = run_pdtm()
    if output is None:
        print(f"{colorize('[ERR]', Colors.ERROR)} pdtm is not installed or not found in PATH.")
        return None

    tools = parse_pdtm_output(output)

    print("\n" + colorize("=== ProjectDiscovery Tools Status ===", Colors.HEADER))
    for tool in sorted(CORE_TOOLS):
        info = tools.get(tool)
        if not info:
            print(f"{colorize('[MISSING]', Colors.ERROR)} {tool}: not installed or not detected")
            continue

        status = info["status"]
        current = info["current_version"]
        latest = info["latest_version"]

        if status == "latest":
            print(f"{colorize('[OK]', Colors.OK)} {tool}: up-to-date ({current})")
        elif status == "outdated":
            print(f"{colorize('[OUTDATED]', Colors.WARN)} {tool}: {current} → {latest}")
        elif status == "not installed":
            print(f"{colorize('[MISSING]', Colors.ERROR)} {tool}: not installed")
        elif status == "not supported":
            print(f"{colorize('[SKIP]', Colors.MUTED)} {tool}: not supported by pdtm")

    return tools

if __name__ == "__main__":
    check_projectdiscovery_tools()
