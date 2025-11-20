import re

def parse_pdtm_output(output: str):
    tools = {}

    # Split output into lines and skip the first 10
    lines = output.splitlines()[9:]
    trimmed_output = "\n".join(lines)

    pattern = re.compile(
        r"^\s*\d+\.\s+([a-zA-Z0-9\-_]+)\s+"           # tool name
        r"\((latest|outdated|not installed|not supported)\)"  # status
        r"(?:\s+\(([\d\.]+)\))?"                       # current version (optional)
        r"(?:\s+➡\s+\(([\d\.]+)\))?",                  # latest version if outdated (optional)
        re.MULTILINE
    )

    for m in pattern.finditer(trimmed_output):
        name = m.group(1)
        status = m.group(2)
        current = m.group(3) if m.group(3) else None
        latest = m.group(4) if m.group(4) else None

        tools[name] = {
            "status": status,
            "current_version": current,
            "latest_version": latest,
        }

    return tools

pdtm_output = r"""
               ____
     ____  ____/ / /_____ ___
    / __ \/ __  / __/ __ __  \
   / /_/ / /_/ / /_/ / / / / /
  / .___/\__,_/\__/_/ /_/ /_/
 /_/

                projectdiscovery.io

[INF] Current pdtm version v0.1.3 (latest)
[INF] [OS: LINUX] [ARCH: AMD64] [GO: 1.24.3]
[INF] Path to download project binary: /home/kali/.pdtm/go/bin
[INF] Path /home/kali/.pdtm/go/bin configured in environment variable $PATH
1. aix (latest) (0.0.5)
2. alterx (latest) (0.0.6)
3. asnmap (latest) (1.1.1)
4. cdncheck (outdated) (1.2.9) ➡ (1.2.10)
5. chaos-client (latest) (0.5.2)
6. cloudlist (latest) (1.2.2)
7. dnsx (latest) (1.2.2)
8. httpx (outdated) (1.7.1) ➡ (1.7.2)
9. interactsh-client (latest) (1.2.4)
10. interactsh-server (latest) (1.2.4)
11. katana (latest) (1.2.2)
12. mapcidr (latest) (1.1.97)
13. naabu (not supported)
14. notify (latest) (1.0.7)
15. nuclei (outdated) (3.4.10) ➡ (3.5.1)
16. pdtm (latest) (0.1.3)
17. proxify (latest) (0.0.16)
18. shuffledns (latest) (1.1.0)
19. simplehttpserver (latest) (0.0.6)
20. subfinder (outdated) (2.9.0) ➡ (2.10.0)
21. tldfinder (latest) (0.0.2)
22. tlsx (outdated) (1.2.1) ➡ (1.2.2)
23. tunnelx (not installed)
24. uncover (latest) (1.1.0)
25. urlfinder (latest) (0.0.3)
26. vulnx (not installed)

"""

# Example usage
parsed = parse_pdtm_output(pdtm_output)  # pass the full pdtm output here
for tool, info in parsed.items():
    print(tool, info)
