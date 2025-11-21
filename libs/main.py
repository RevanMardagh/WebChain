# __main__.py
from input_parser import parse_arguments
from check_versions import check_projectdiscovery_tools
from install_dependencies import prompt_and_install
from pipeline import run_recon
from utils import colorize, Colors

def main():
    args = parse_arguments()

    tools = check_projectdiscovery_tools()
    if tools:
        # prompt/install only for required tools; respects dry-run
        prompt_and_install(tools, dry_run=args.dry_run)

    # run single domain
    if args.domain:
        run_recon(args.domain, args.out, proxy=args.proxy, dry_run=args.dry_run)

    # run domains from file
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8", errors="ignore") as f:
            domains = [line.strip() for line in f if line.strip()]
        for domain in domains:
            run_recon(domain, args.out, proxy=args.proxy, dry_run=args.dry_run)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colorize("\n[INFO] Interrupted by user. Exiting.", Colors.WARN))
