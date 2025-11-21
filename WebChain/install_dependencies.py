import subprocess
from check_versions import check_projectdiscovery_tools
from utils import colorize, Colors

REQUIRED_TOOLS = ["subfinder", "dnsx", "naabu", "httpx", "katana"]


def run_cmd(cmd: list, dry_run: bool = False):
    """Helper to run or simulate shell commands."""
    if dry_run:
        print(colorize(f"[DRY-RUN] Would execute: {' '.join(cmd)}", Colors.MUTED))
        return

    print(colorize(f"[INFO] Executing: {' '.join(cmd)}", Colors.INFO))

    try:
        subprocess.run(cmd, check=True)
        print(colorize("[SUCCESS] Command executed successfully.", Colors.OK))
    except subprocess.CalledProcessError:
        print(colorize(f"[ERROR] Command failed: {' '.join(cmd)}", Colors.ERROR))
    except FileNotFoundError:
        print(colorize(f"[ERROR] Binary not found: {cmd[0]}", Colors.ERROR))


def install_tool(tool_name: str, dry_run: bool = False):
    """Install a missing tool."""
    if tool_name == "naabu":
        cmd = ["sudo", "apt", "install", "naabu", "-y"]
    else:
        cmd = ["pdtm", "-i", tool_name]

    run_cmd(cmd, dry_run)


def update_tool(tool_name: str, dry_run: bool = False):
    """Update an outdated tool."""
    if tool_name == "naabu":
        cmd = ["naabu", "-up"]
    else:
        cmd = ["pdtm", "-u", tool_name]

    run_cmd(cmd, dry_run)


def prompt_and_install(tools: dict, dry_run: bool = False):
    """Check required PD tools and install/update them."""
    actions = []  # Will contain tuples: ("install"|"update", tool_name)

    for tool in REQUIRED_TOOLS:
        if tool not in tools:
            print(colorize(f"[WARN] {tool} not found in pdtm output.", Colors.WARN))
            continue

        status = tools[tool]["status"]

        if status == "not installed":
            actions.append(("install", tool))
        elif status == "outdated":
            actions.append(("update", tool))

    if not actions:
        print(colorize("[INFO] All required tools are installed and up-to-date.", Colors.INFO))
        return

    print("\n" + colorize("The following required tools need attention:", Colors.HEADER))
    for action, t in actions:
        info = tools[t]
        if action == "install":
            print(f"- {t}: not installed")
        else:
            print(f"- {t}: {info['current_version']} → {info['latest_version']}")

    # Auto-run in dry mode, no prompt
    if dry_run:
        print(colorize("\n[DRY-RUN] Skipping user prompt — simulation only.", Colors.MUTED))
        for action, t in actions:
            if action == "install":
                install_tool(t, dry_run=True)
            else:
                update_tool(t, dry_run=True)
        return

    choice = input(
        "\nDo you want to automatically install/update these tools? [y/N]: "
    ).strip().lower()

    if choice != "y":
        print(colorize("[INFO] Skipping installation/update.", Colors.INFO))
        return

    # Perform actual install/update
    for action, t in actions:
        if action == "install":
            install_tool(t, dry_run)
        else:
            update_tool(t, dry_run)


if __name__ == "__main__":
    tools = check_projectdiscovery_tools()
    dry_run = True  # Example dry-run
    prompt_and_install(tools, dry_run=dry_run)
