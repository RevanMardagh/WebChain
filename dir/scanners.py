import subprocess


def run_command(cmd: list, dry_run: bool = False):
    """
    Executes a shell command.
    If dry_run=True, prints the command and returns.
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


def run_subfinder(domain: str, output: str, dry_run=False):
    cmd = [
        "subfinder",
        "-silent",
        "-d", domain,
        "-o", output,
    ]
    run_command(cmd, dry_run=dry_run)


def run_dnsx(input_file: str, output: str, dry_run=False):
    cmd = [
        "dnsx",
        "-silent",
        "-resp",
        "-r", "8.8.8.8",
        "-l", input_file,
        "-o", output
    ]
    run_command(cmd, dry_run=dry_run)


def run_naabu(input_file: str, output: str, dry_run=False):
    cmd = [
        "naabu",
        "-silent",
        "-list", input_file,
        "-o", output
    ]
    run_command(cmd, dry_run=dry_run)


def run_httpx(input_file: str, output: str, proxy=None, dry_run=False):
    cmd = [
        "httpx",
        "-silent",
        "-l", input_file,
        "-o", output
    ]

    if proxy:
        cmd += ["-proxy", f"http://{proxy}"]

    run_command(cmd, dry_run=dry_run)

def run_katana(input_file: str, output: str, proxy=None, dry_run=False):
    cmd = [
        "katana",
        "-silent",
        "-list", input_file,
        "-o", output
    ]

    if proxy:
        cmd += ["-proxy", f"http://{proxy}"]

    run_command(cmd, dry_run=dry_run)


def run_recon(domain: str, out_dir: str, proxy=None, dry_run=False):
    print(f"\n[INFO] Starting recon for: {domain}")

    # File paths
    subfinder_out = f"{out_dir}/{domain}/subfinder.txt"
    dnsx_out      = f"{out_dir}/{domain}/dnsx.txt"
    naabu_out     = f"{out_dir}/{domain}/naabu.txt"
    httpx_out     = f"{out_dir}/{domain}/httpx.txt"
    katana_out    = f"{out_dir}/{domain}/katana.txt"

    # 1. subfinder
    run_subfinder(domain, subfinder_out, dry_run)

    # 2. dnsx
    run_dnsx(subfinder_out, dnsx_out, dry_run)

    # 3. naabu
    run_naabu(dnsx_out, naabu_out, dry_run)

    # 4. httpx
    run_httpx(naabu_out, httpx_out, proxy=proxy, dry_run=dry_run)

    # 5. katana
    run_katana(httpx_out, katana_out, proxy=proxy, dry_run=dry_run)

    print(f"[INFO] Recon finished for {domain}\n")

