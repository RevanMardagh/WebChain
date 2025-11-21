  

# WebChain - ProjectDiscovery tool automation

Web application enumeration toolchain that chains Project Discovery utilities into a single workflow

  ---

## ⭐ Features

### 🔗 Full Recon Pipeline

  Runs the complete ProjectDiscovery tool-chain:

- **subfinder** — discover subdomains
- **dnsx** — DNS resolution
- **naabu** — port scanning
- **httpx** — detect live web services
- **katana** — crawl for URLs/endpoints  

Each stage uses pretty CLI formatting with colors and sample output previews

---

### 🤖 Optional AI Analysis (`-ai`)

Katana results can be automatically analyzed using **Google Gemini**.

AI provides:

- Potential high-value endpoints
- Advisory notes for manual testing
- A short security summary

AI **never** executes attacks or suggests exploits.


---

### 🔧 Dependency management

WebChain can:
- Detect installed/missing ProjectDiscovery tools
- Detect outdated versions
- Install missing tools
- Update existing tools

---

### 🧪 Dry-run mode `--dry-run`

Simulate command execution without running anything

---

## Installation

- Clone the repository

```bash
git clone https://github.com/RevanMardagh/WebChain
cd WebChain
```

### Run as a Python file

Run `main.py`

```bash
python WebChain/main.py --help
```

### Run prebuilt binary

```
./compiled/Webchain --help
```


