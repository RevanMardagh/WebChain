from taking_input import parse_arguments
from check_versions import check_projectdiscovery_tools
from install_dependencies import prompt_and_install
from pipeline import run_recon

def main():
    args = parse_arguments()

    tools = check_projectdiscovery_tools()
    if tools:
        prompt_and_install(tools, dry_run=args.dry_run)

    if args.domain:
        run_recon(args.domain, args.out, proxy=args.proxy, dry_run=args.dry_run)

    if args.input_file:
        with open(args.input_file, "r") as f:
            domains = [line.strip() for line in f if line.strip()]
        for domain in domains:
            run_recon(domain, args.out, proxy=args.proxy, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
