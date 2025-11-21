# steps/subdomain_enum.py
from pathlib import Path
from runner import run_command
import sys

def run_subfinder(domain: str, out_dir: Path, dry_run: bool = False) -> Path:
    output_file = out_dir / "01_subfinder.txt"

    cmd = [
        "subfinder",
        "-d", domain,
        "-silent",
        "-o", str(output_file)
    ]

    print(f"\n[1] Running subfinder on {domain}...")
    run_command(cmd, dry_run)

    if not dry_run and not output_file.exists():
        print("[ERROR] subfinder failed to create output file.")
        sys.exit(1)

    if not dry_run:
        lines = [l for l in output_file.read_text().splitlines() if l.strip()]
        print(f"[OK] Found {len(lines)} subdomains → {output_file.name}")
    else:
        print("[INFO] (dry-run) subfinder output would be saved to 01_subfinder.txt")

    return output_file


def run_dnsx(subfinder_file: Path, out_dir: Path, dry_run: bool = False) -> Path:
    resolved_file = out_dir / "02_dnsx_resolved.txt"

    cmd = [
        "dnsx",
        "-l", str(subfinder_file),
        "-silent",
        "-a", "-aaaa", "-cname",
        "-resp-only",
        "-o", str(resolved_file)
    ]

    print(f"[2] Resolving with dnsx...")
    run_command(cmd, dry_run)

    if not dry_run and resolved_file.exists() and resolved_file.stat().st_size > 0:
        lines = resolved_file.read_text().splitlines()
        live_count = len([l for l in lines if l.strip()])
        print(f"[OK] {live_count} hosts resolved → {resolved_file.name}")
    elif not dry_run:
        print("[WARN] No live hosts after dnsx. Stopping early.")
        sys.exit(0)

    return resolved_file