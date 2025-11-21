# input_parser.py
import argparse
import os
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="ProjectDiscovery Recon Automation (subfinder → dnsx → naabu → httpx → katana)"
    )

    parser.add_argument("-d", "--domain", help="Single domain or subdomain (example.com)")
    parser.add_argument("-i", "--input-file", help="File containing one domain per line")
    parser.add_argument("-o", "--out", default="recon-output", help="Output directory (default: recon-output)")
    parser.add_argument("--proxy", nargs="?", const="127.0.0.1:8080", default=None,
                        help="BurpSuite proxy address (default when empty: 127.0.0.1:8080)")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without executing them")

    parser.add_argument(
        "-ai",
        "--ai_overview",
        action="store_true",
        help="Send discovered URLs to Google Gemini for analysis"
    )

    args = parser.parse_args()

    if not args.domain and not args.input_file:
        print("[ERROR] You must provide either --domain or --input-file")
        sys.exit(1)

    if args.input_file and not os.path.isfile(args.input_file):
        print(f"[ERROR] Input file not found: {args.input_file}")
        sys.exit(1)

    if not os.path.exists(args.out):
        try:
            os.makedirs(args.out, exist_ok=True)
            print(f"[INFO] Created output directory: {args.out}")
        except Exception as e:
            print(f"[ERROR] Failed to create output directory: {e}")
            sys.exit(1)

    return args

if __name__ == "__main__":
    args = parse_arguments()
    print("[INFO] User provided options:")
    print(args)
