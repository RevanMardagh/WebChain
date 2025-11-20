import subprocess
from check_versions import check_projectdiscovery_tools

REQUIRED_TOOLS = ["subfinder", "dnsx", "naabu", "httpx", "katana"]


def install_tool(tool_name: str, dry_run: bool = False):
    """
    Install a ProjectDiscovery tool.
    Supports dry-run mode which prints the command instead of running it.
    """
    if tool_name == "naabu":
        cmd = ["sudo", "apt", "install", "naabu", "-y"]
    else:
        cmd = ["pdtm", "-i", tool_name]

    if dry_run:
        print(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
        return

    try:
        print(f"[INFO] Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"[SUCCESS] {tool_name} installed/updated.")
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to install {tool_name}.")


def prompt_and_install(tools: dict, dry_run: bool = False):
    """
    Prompt user to install/update ONLY required tools.
    Respects dry-run mode.
    """
    tools_to_install = []

    for tool in REQUIRED_TOOLS:
        if tool not in tools:
            print(f"[WARN] {tool} not found in pdtm output.")
            continue

        status = tools[tool]["status"]
        if status in ["outdated", "not installed"]:
            tools_to_install.append(tool)

    if not tools_to_install:
        print("[INFO] Required tools are already installed and up-to-date.")
        return

    print("\nThe following required tools are outdated or missing:")
    for t in tools_to_install:
        info = tools[t]
        status = info["status"]
        if status == "outdated":
            print(f"- {t}: {info['current_version']} → {info['latest_version']}")
        else:
            print(f"- {t}: not installed")

    if dry_run:
        print("\n[DRY-RUN] Skipping user prompt — this is a simulation.")
        for t in tools_to_install:
            install_tool(t, dry_run=True)
        return

    choice = input("\nDo you want to automatically install/update these tools? [y/N]: ").strip().lower()
    if choice != "y":
        print("[INFO] Skipping installation/update.")
        return

    for t in tools_to_install:
        install_tool(t, dry_run=dry_run)

if __name__ == "__main__":
    tools = check_projectdiscovery_tools()

    # Example: enable dry-run mode
    dry_run = True

    prompt_and_install(tools, dry_run=dry_run)
