# pipeline.py
from utils import run_command, colorize, Colors
import os
from collections import defaultdict
# from ai_overview import generate_ai_overview

# Helper to pretty header
def header(title: str):
    print(colorize("\n" + "─" * 60, Colors.MUTED))
    print(colorize(f"▶ {title}", Colors.HEADER))
    print(colorize("─" * 60, Colors.MUTED))

def print_sample_output(stdout: str, max_lines: int = 10):
    if not stdout:
        print(colorize("[no output captured]", Colors.MUTED))
        return
    lines = [l.rstrip() for l in stdout.splitlines() if l.strip()]
    if not lines:
        print(colorize("[no output captured]", Colors.MUTED))
        return
    for i, line in enumerate(lines):
        if i >= max_lines:
            print(colorize(f"... ({len(lines)-max_lines} more lines)", Colors.MUTED))
            break
        print(line)

def safe_read_lines(path: str):
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [l.strip() for l in f if l.strip()]


def run_subfinder(domain: str, output: str, dry_run=False):
    header("subfinder (discovering subdomains)")
    cmd = ["subfinder", "-silent", "-d", domain, "-o", output]
    stdout = run_command(cmd, dry_run=dry_run)
    # If stdout empty (non-dry), try reading the output file for live lines
    if not stdout and not dry_run:
        stdout = "\n".join(safe_read_lines(output))

    # --- Ensure root domain is included ---
    subs = safe_read_lines(output)
    if domain not in subs:
        subs.append(domain)
        with open(output, "w") as f:
            f.write("\n".join(subs))
        if not dry_run:
            stdout += f"\n{domain}"

    print_sample_output(stdout)
    # summary
    print(colorize(f"\n✔ subfinder completed", Colors.OK))
    print(f"   • Domains discovered: {len(subs)}")
    print(f"   • Output saved: {output}")


def run_dnsx(input_file: str, output: str, dry_run=False):
    header("dnsx (resolving subdomains)")
    cmd = ["dnsx", "-silent", "-r", "8.8.8.8", "-l", input_file, "-o", output]
    stdout = run_command(cmd, dry_run=dry_run)
    if not stdout and not dry_run:
        stdout = "\n".join(safe_read_lines(output))
    # Print sample resolved lines
    print_sample_output(stdout)
    # summary
    lines = safe_read_lines(output)
    print(colorize(f"\n✔ dnsx completed", Colors.OK))
    print(f"   • Alive hosts: {len(lines)}")
    print(f"   • Output saved: {output}")

def run_naabu(input_file: str, output: str, dry_run=False):
    header("naabu (port scanning)")
    cmd = ["naabu", "-silent","-list", input_file, "-o", output]
    stdout = run_command(cmd, dry_run=dry_run)
    if not stdout and not dry_run:
        stdout = "\n".join(safe_read_lines(output))
    print_sample_output(stdout)
    # summary: count unique hosts with open ports (format ip:port or host:port)
    lines = safe_read_lines(output)
    unique_hosts = set()
    for l in lines:
        # naive split on ':' to get host (works for ip:port and host:port)
        parts = l.split(":")
        if parts:
            unique_hosts.add(parts[0])
    print(colorize(f"\n✔ naabu completed", Colors.OK))
    print(f"   • Hosts with open ports: {len(unique_hosts)}")
    print(f"   • Output saved: {output}")

def run_httpx(input_file: str, output: str, proxy=None, dry_run=False):
    header("httpx (probing web services)")
    cmd = ["/home/kali/.pdtm/go/bin/httpx", "-silent", "-list", input_file, "-o", output]
    if proxy:
        cmd += ["-proxy", f"http://{proxy}"]
    stdout = run_command(cmd, dry_run=dry_run)
    if not stdout and not dry_run:
        stdout = "\n".join(safe_read_lines(output))
    print_sample_output(stdout)
    lines = safe_read_lines(output)
    print(colorize(f"\n✔ httpx completed", Colors.OK))
    print(f"   • Web services detected: {len(lines)}")
    print(f"   • Output saved: {output}")

def run_katana(input_file: str, output: str, proxy=None, dry_run=False):
    header("katana (crawling URLs)")
    cmd = ["katana", "-silent", "-jc", "-kf", "all", "-list", input_file, "-o", output]
    if proxy:
        cmd += ["-proxy", f"http://{proxy}"]
    stdout = run_command(cmd, dry_run=dry_run)
    if not stdout and not dry_run:
        stdout = "\n".join(safe_read_lines(output))
    print_sample_output(stdout, max_lines=15)
    lines = safe_read_lines(output)
    print(colorize(f"\n✔ katana completed", Colors.OK))
    print(f"   • URLs extracted: {len(lines)}")
    print(f"   • Output saved: {output}")

def run_recon(domain: str, out_dir: str, proxy=None, dry_run=False):
    """
    Run the full chain for one domain:
    subfinder -> dnsx -> naabu -> httpx -> katana
    """
    # normalize domain filename (replace slashes if any)
    safe_domain = domain.replace("/", "_")
    subfinder_out = os.path.join(out_dir, f"{safe_domain}/subfinder.txt")
    dnsx_out      = os.path.join(out_dir, f"{safe_domain}/dnsx.txt")
    naabu_out     = os.path.join(out_dir, f"{safe_domain}/naabu.txt")
    httpx_out     = os.path.join(out_dir, f"{safe_domain}/httpx.txt")
    katana_out    = os.path.join(out_dir, f"{safe_domain}/katana.txt")

    print(colorize(f"\n=== Starting recon for: {domain} ===", Colors.HEADER))
    run_subfinder(domain, subfinder_out, dry_run=dry_run)
    run_dnsx(subfinder_out, dnsx_out, dry_run=dry_run)
    run_naabu(dnsx_out, naabu_out, dry_run=dry_run)
    run_httpx(naabu_out, httpx_out, proxy=proxy, dry_run=dry_run)
    run_katana(httpx_out, katana_out, proxy=proxy, dry_run=dry_run)
    print(colorize(f"\n=== Recon finished for: {domain} ===", Colors.OK))
