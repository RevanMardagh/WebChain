# input_parser.py
import argparse
import os
import sys
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="pdrecon — Automated ProjectDiscovery chain → BurpSuite ready"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Single domain (e.g. tesla.com)")
    group.add_argument("-l", "--list", dest="input_file", help="File with one domain per line")

    parser.add_argument("-o", "--output", default="recon-output", help="Output base directory")
    parser.add_argument("--proxy", default=None, help="BurpSuite proxy (e.g. 127.0.0.1:8080)")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without running")

    args = parser.parse_args()

    # Validation
    if args.input_file and not Path(args.input_file).is_file():
        print(f"[ERROR] Input file not found: {args.input_file}")
        sys.exit(1)

    Path(args.output).mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Results will be saved to: {args.output}")

    return args