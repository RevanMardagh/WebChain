#!/usr/bin/env python3
# pdrecon.py
from pathlib import Path
import sys

from input_parser import parse_arguments
from check_versions import check_projectdiscovery_tools
from subdomain_enum import run_subfinder, run_dnsx

def process_domain(domain: str, base_out_dir: Path, dry_run: bool):
    domain_dir = base_out_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*20} TARGET: {domain} {'='*20}")

    subfinder_file = run_subfinder(domain, domain_dir, dry_run)
    resolved_file = run_dnsx(subfinder_file, domain_dir, dry_run)

    print(f"\n[SUCCESS] Subdomain enumeration complete for {domain}!")
    print(f"    Next → naabu → httpx → katana")
    print(f"    Results: {domain_dir}/\n")


def main():
    print("""
    PDR E C O N
    Subdomain Discovery → BurpSuite Ready
    """)

    args = parse_arguments()

    # Check tools
    tools_status = check_projectdiscovery_tools()
    if not tools_status:
        print("[ERROR] Tool check failed. Install pdtm and required tools.")
        sys.exit(1)

    # Get domains
    domains = []
    if args.domain:
        domains = [args.domain.strip()]
    else:
        with open(args.input_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    domains.append(line)

    # Run for each domain
    for domain in domains:
        process_domain(domain, Path(args.output), args.dry_run)

    if args.dry_run:
        print("[INFO] Dry-run complete. No files were written.")
    else:
        print(f"[SUCCESS] All done! Check results in: {args.output}/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user.")
        sys.exit(0)