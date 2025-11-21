#!/usr/bin/env python3
"""
pdrecon - ProjectDiscovery Recon Chain for BurpSuite
Chains: subfinder → dnsx → naabu → httpx → katana
Automatically sends all HTTP traffic through BurpSuite for instant manual testing.
"""

import argparse
import os
import sys
import subprocess
import signal
import json
from datetime import datetime
from pathlib importlib.util
import find_spec
from pathlib import Path

# ----------------------------- CONFIG -----------------------------
CORE_TOOLS = ["subfinder", "dnsx", "naabu", "httpx", "katana"]
WEB_PORTS = "80,443,8080,8443,8000,3000,5000,8081,9000,9443"


# -----------------------------------------------------------------

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_info(msg):    print(f"{Colors.CYAN}[*]{Colors.RESET} {msg}")


def print_success(msg): print(f"{Colors.GREEN}[+]{Colors.RESET} {msg}")


def print_warning(msg): print(f"{Colors.YELLOW}[!]{Colors.RESET} {msg}")


def print_error(msg):   print(f"{Colors.RED}[-]{Colors.RESET} {msg}")


# -------------------------- TOOL CHECK ---------------------------
def check_tools():
    print_info("Checking ProjectDiscovery tools via pdtm...")
    try:
        result = subprocess.run(
            ["pdtm", "-installed"], capture_output=True, text=True, check=False
        )
        installed = result.stdout.strip().splitlines()
        missing = [t for t in CORE_TOOLS if t not in " ".join(installed)]
        if missing:
            print_error(f"Missing tools: {', '.join(missing)}")
            print_info("Install with: pdtm -install " + " ".join(missing))
            sys.exit(1)
        print_success("All required tools are installed!")
    except FileNotFoundError:
        print_error("pdtm not found. Install it from https://github.com/projectdiscovery/pdtm")
        sys.exit(1)


# ------------------------- COMMAND RUNNER ------------------------
def run_command(cmd, dry_run=False, capture=False):
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    print(f"{Colors.GRAY}→ {cmd_str}{Colors.RESET}"

    if dry_run:
        return ""

    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=capture,
            text=True,
            env=os.environ
        )
        if capture:
            return result.stdout
        if result.returncode != 0:
            print_warning(f"Command failed (exit {result.returncode}), continuing...")
        return result.stdout
    except Exception as e:
        print_error(f"Command failed: {e}")
        return ""


# --------------------------- MAIN LOGIC --------------------------
def process_domain(domain: str, out_dir: Path, proxy: str, dry_run: bool):
    domain_clean = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
    work_dir = out_dir / domain_clean
    work_dir.mkdir(parents=True, exist_ok=True)

    print_success(f"\nStarting recon on {domain_clean}")
    print_info(f"Results → {work_dir}\n")

    # Set proxy for httpx & katana
    if proxy:
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy
        print_info(f"BurpSuite proxy enabled: {proxy}")

    # 1. Subfinder
    sub_file = work_dir / "01_subfinder.txt"
    if not sub_file.exists() or sub_file.stat().st_size == 0:
        cmd = ["subfinder", "-d", domain_clean, "-silent", "-o", str(sub_file)]
        run_command(cmd, dry_run)
    else:
        print_info("Subfinder results already exist, skipping...")

    # 2. dnsx - resolve + filter live
    dnsx_file = work_dir / "02_dnsx_resolved.txt"
    if not dnsx_file.exists() or dnsx_file.stat().st_size == 0:
        cmd = f"cat {sub_file} | dnsx -silent -a -resp-only -o {dnsx_file}"
        run_command(cmd, dry_run)
    else:
        print_info("dnsx results already exist, skipping...")

    # 3. naabu - port scan
    naabu_file = work_dir / "03_naabu_ports.txt"
    if not naabu_file.exists() or naa_file.stat().st_size == 0:
        cmd = [
            "naabu", "-list", str(dnsx_file), "-p", WEB_PORTS,
            "-silent", "-o", str(naabu_file), "-exclude-ports", "80,443"
        ]
        run_command(cmd, dry_run)
        # Always include original 80/443 from dnsx
        with open(naabu_file, "a") as f:
            for line in open(dnsx_file):
                host = line.strip().split()[0] if line.strip() else ""
                if host:
                    f.write(f"{host}:443\n")
                    f.write(f"{host}:80\n")
    else:
        print_info("naabu results already exist, skipping...")

    # 4. httpx - probe live HTTP(s)
    httpx_file = work_dir / "04_httpx_live.txt"
    if not httpx_file.exists() or httpx_file.stat().st_size == 0:
        proxy_flag = ["-http-proxy", proxy] if proxy else []
        cmd = [
                  "httpx", "-list", str(naabu_file), "-silent",
                  "-title", "-tech-detect", "-status-code", "-follow-redirects",
                  "-o", str(httpx_file)
              ] + proxy_flag
        run_command(cmd, dry_run)
    else:
        print_info("httpx results already exist, skipping...")

    # 5. katana - deep crawl
    katana_file = work_dir / "05_katana_endpoints.txt"
    final_urls = work_dir / "final_urls.txt"
    if not katana_file.exists() or katana_file.stat().st_size == 0:
        proxy_flag = ["-proxy", proxy] if proxy else []
        depth = ["-depth", "4"]
        extras = ["-known-files", "all", "-extension", ".js,.json,.xml,.txt"]
        cmd = [
                  "katana", "-list", str(httpx_file),
                  "-silent", "-headless", "-automatic-form-fill",
                  "-output", str(katana_file)
              ] + depth + extras + proxy_flag
        run_command(cmd, dry_run)

        # Save clean list for Burp
        run_command(f"cat {katana_file} | sort -u > {final_urls}", dry_run)
    else:
        print_info("katana results already exist, skipping...")

    # Summary
    summary = {
        "target": domain_clean,
        "timestamp": datetime.now().isoformat(),
        "proxy_used": proxy or "none",
        "counts": {}
    }
    for name, path in [
        ("subdomains", sub_file),
        ("resolved", dnsx_file),
        ("ports_found", naabu_file),
        ("live_web", httpx_file),
        ("endpoints", katana_file or final_urls),
    ]:
        try:
            count = len([l for l in open(path) if l.strip()])
            summary["counts"][name] = count
        except:
            summary["counts"][name] = 0

    (work_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print_success(f"\nRecon complete for {domain_clean}!")
    print_success(f"Total endpoints discovered: {summary['counts'].get('endpoints', 0)}")
    print_info(f"Open in BurpSuite → Target → Site map → {domain_clean}")
    print_info(f"Or import {final_urls} into Scope")


# -------------------------- ARG PARSER ---------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="pdrecon - Full PD chain → BurpSuite ready")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Single domain (e.g. example.com)")
    group.add_argument("-i", "--input-file", help="File with one domain per line")

    parser.add_argument("-o", "--out", default="recon-output", help="Output base directory")
    parser.add_argument("--proxy", default="127.0.0.1:8080", help="Burp proxy (default: 127.0.0.1:8080)")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy (override default)")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without executing")

    return parser.parse_args()


# ---------------------------- MAIN -----------------------------
def main():
    print(f"""{Colors.BOLD}
    ╔══════════════════════════════════════╗
    ║          PDRecon → BurpSuite         ║          ║
    ║  subfinder → dnsx → naabu → httpx → katana  ║
    ╚══════════════════════════════════════╝{Colors.RESET}\n""")

    args = parse_args()

    # Handle proxy
    proxy = None
    if not args.no_proxy:
        proxy = args.proxy

    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    if args.dry_run:
        print_warning("DRY RUN MODE — NO COMMANDS WILL BE EXECUTED\n")

    check_tools()

    domains = []
    if args.domain:
        domains = [args.domain]
    else:
        try:
            domains = [line.strip() for line in open(args.input_file) if line.strip()]
        except Exception as e:
            print_error(f"Failed to read input file: {e}")
            sys.exit(1)

    print_info(f"Processing {len(domains)} domain(s)\n")

    for domain in domains:
        try:
            process_domain(domain, out_dir, proxy, args.dry_run)
        except KeyboardInterrupt:
            print_error("\nInterrupted by user")
            sys.exit(1)
        except Exception as e:
            print_error(f"Error processing {domain}: {e}")

    print_success("\nAll done! Happy hacking!")


if __name__ == "__main__":
    main()