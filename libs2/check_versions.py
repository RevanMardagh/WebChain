import subprocess
import re

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

    # Remove ANSI escape codes
    clean_output = ansi_escape.sub("", output)
    clean_output = clean_output.replace("\r\n", "\n").replace("\r", "\n")

    # Only keep lines that start with a number followed by a dot
    lines = [line for line in clean_output.splitlines() if re.match(r"^\s*\d+\.", line)]
    trimmed_output = "\n".join(lines)

    pattern = re.compile(
        r"^\s*\d+\.\s+([a-zA-Z0-9\-_]+)\s+"           # tool name
        r"\((latest|outdated|not installed|not supported)\)"  # status
        r"(?:\s+\(([\d\.]+)\))?"                       # current version (optional)
        r"(?:\s+➡\s+\(([\d\.]+)\))?",                  # latest version if outdated (optional)
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

# ANSI color codes
class Colors:
    OK = "\033[92m"        # green
    OUTDATED = "\033[93m"  # yellow
    MISSING = "\033[91m"   # red
    SKIP = "\033[90m"      # gray
    RESET = "\033[0m"      # reset

# Only show these tools
CORE_TOOLS = {"subfinder", "dnsx", "naabu", "httpx", "katana"}

def check_projectdiscovery_tools():
    output = run_pdtm()
    if output is None:
        print(f"{Colors.MISSING}[ERR]{Colors.RESET} pdtm is not installed or not found in PATH.")
        return None

    tools = parse_pdtm_output(output)

    print("\n=== ProjectDiscovery Tools Status ===")
    for tool in CORE_TOOLS:
        info = tools.get(tool)
        if not info:
            # If tool is completely missing from output
            print(f"{Colors.MISSING}[MISSING]{Colors.RESET} {tool}: not installed or not detected")
            continue

        status = info["status"]
        current = info["current_version"]
        latest = info["latest_version"]

        if status == "latest":
            print(f"{Colors.OK}[OK]{Colors.RESET} {tool}: up-to-date ({current})")
        elif status == "outdated":
            print(f"{Colors.OUTDATED}[OUTDATED]{Colors.RESET} {tool}: {current} → {latest}")
        elif status == "not installed":
            print(f"{Colors.MISSING}[MISSING]{Colors.RESET} {tool}: not installed")
        elif status == "not supported":
            print(f"{Colors.SKIP}[SKIP]{Colors.RESET} {tool}: not supported by pdtm")

    return tools

if __name__ == "__main__":
    check_projectdiscovery_tools()
