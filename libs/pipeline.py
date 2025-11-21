from utils import run_command

def run_subfinder(domain: str, output: str, dry_run=False):
    cmd = ["subfinder", "-silent", "-d", domain, "-o", output]
    run_command(cmd, dry_run=dry_run)

def run_dnsx(input_file: str, output: str, dry_run=False):
    cmd = ["dnsx", "-silent", "-r", "8.8.8.8", "-l", input_file, "-o", output]
    run_command(cmd, dry_run=dry_run)

def run_naabu(input_file: str, output: str, dry_run=False):
    cmd = ["naabu", "-silent", "-p", "80,443,8080,8443", "-list", input_file, "-o", output]
    run_command(cmd, dry_run=dry_run)

def run_httpx(input_file: str, output: str, proxy=None, dry_run=False):
    cmd = ["httpx", "-silent", "-l", input_file, "-o", output]
    if proxy:
        cmd += ["-proxy", f"http://{proxy}"]
    run_command(cmd, dry_run=dry_run)

def run_katana(input_file: str, output: str, proxy=None, dry_run=False):
    cmd = ["katana", "-silent", "-list", input_file, "-o", output]
    if proxy:
        cmd += ["-proxy", f"http://{proxy}"]
    run_command(cmd, dry_run=dry_run)

def run_recon(domain: str, out_dir: str, proxy=None, dry_run=False):
    print(f"\n[INFO] Starting recon for: {domain}")

    subfinder_out = f"{out_dir}/{domain}_subfinder.txt"
    dnsx_out      = f"{out_dir}/{domain}_dnsx.txt"
    naabu_out     = f"{out_dir}/{domain}_naabu.txt"
    httpx_out     = f"{out_dir}/{domain}_httpx.txt"
    katana_out    = f"{out_dir}/{domain}_katana.txt"

    run_subfinder(domain, subfinder_out, dry_run=dry_run)
    run_dnsx(subfinder_out, dnsx_out, dry_run=dry_run)
    run_naabu(dnsx_out, naabu_out, dry_run=dry_run)
    run_httpx(naabu_out, httpx_out, proxy=proxy, dry_run=dry_run)
    run_katana(httpx_out, katana_out, proxy=proxy, dry_run=dry_run)

    print(f"[INFO] Recon finished for {domain}\n")
