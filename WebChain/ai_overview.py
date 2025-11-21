# ai_overview.py
from google import genai
from utils import colorize, Colors
import os


def generate_ai_overview_from_file(output_dir: str, api_key: str) -> str:
    """
    Sends URLs discovered by katana (stored in a file) to Google Gemini
    for high-value endpoint analysis.

    :param katana_file_path: Path to the katana output file (e.g., katana.txt)
    :param api_key: Google GenAI API key
    :return: Raw JSON response from Gemini or an error message
    """
    katana_file_path = os.path.join(output_dir, "katana.txt")
    if not os.path.exists(katana_file_path):
        return colorize(f"[ERROR] Katana output file not found: {katana_file_path}", Colors.ERROR)

    # Read URLs
    with open(katana_file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        return colorize("[WARN] No URLs found in katana output.", Colors.WARN)

    url_list_str = "\n".join(urls)

    prompt = f"""
You are a security analysis assistant. 
You will receive a list of URLs/endpoints discovered during reconnaissance.

### Your Task
- Analyze the URLs.
- Identify which endpoints are **potentially high-value** for manual security testing.
- High-value examples include:
  - Authentication interfaces (e.g., /login, /signin, /auth)
  - Administrative panels (e.g., /admin, /dashboard)
  - File upload points (e.g., /upload, /file/upload)
  - API endpoints (e.g., /api/*)
  - Sensitive configuration or debug pages (e.g., /debug, /config)


### Input URLs:
{url_list_str}

### Output Format (JSON exactly like this):
{{
  "high_value_endpoints": [
    {{
      "url": "<full-url>",
      "reason": "<why this endpoint might be important>"
    }}
  ],
  "summary": "<short and simple textual summary>"
}}
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Get the text, or a fallback message
        text_to_write = response.text or "No response text returned."
        output_file = os.path.join(output_dir, "ai_overview.json")

        # Write to the file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text_to_write)

        return text_to_write

    except Exception:
        return colorize("You've disabled AI, or Google Gemini servers are unavailable.", Colors.ERROR)
