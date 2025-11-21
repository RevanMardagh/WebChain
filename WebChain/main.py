# __main__.py
from input_parser import parse_arguments
from check_versions import check_projectdiscovery_tools
from install_dependencies import prompt_and_install
from pipeline import run_recon
from utils import colorize, Colors
from config import load_config
from ai_overview import  generate_ai_overview_from_file
import os

config = load_config()
API_KEY = config.get("gemini_api_key", "")

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


    if args.ai_overview:
        config = load_config(require_ai=True)
        API_KEY = config.get("gemini_api_key", "")
        if not API_KEY:
            print(colorize("[ERROR] -ai flag used but no Gemini API key found!", Colors.ERROR))
        else:
            output_dir = os.path.join(args.out, args.domain)
            print(colorize("[INFO] Running AI endpoint analysis...", Colors.INFO))
            from ai_overview import generate_ai_overview_from_file
            result = generate_ai_overview_from_file(output_dir, API_KEY)
            print(colorize("\n[AI RESULT]", Colors.HEADER))
            print(result)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colorize("\n[INFO] Interrupted by user. Exiting.", Colors.WARN))
