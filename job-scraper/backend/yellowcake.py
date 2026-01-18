import os
import sys
import requests

if len(sys.argv) < 2:
    print("Usage: python yellowcake_test.py <job_site_url>")
    sys.exit(1)

job_site_url = sys.argv[1]

YELLOWCAKE_API_KEY = os.getenv("YELLOWCAKE_API_KEY")
if not YELLOWCAKE_API_KEY:
    raise RuntimeError("YELLOWCAKE_API_KEY not set")

payload = {
    "url": job_site_url,
    "prompt": (
        "Extract all job listings and return a JSON array with fields: "
        "title, company, location, posting_date, apply_url."
    )
}

headers = {
    "Content-Type": "application/json",
    "X-API-Key": YELLOWCAKE_API_KEY
}

response = requests.post(
    "https://api.yellowcake.dev/v1/extract-stream",
    headers=headers,
    json=payload,
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode("utf-8"))

