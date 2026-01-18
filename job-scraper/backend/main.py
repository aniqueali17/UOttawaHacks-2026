import os
import sys
import json
import subprocess

from urllib.parse import urlparse
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv


from pathlib import Path
# load_dotenv(Path(__file__).with_name(".env"))


load_dotenv()

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "yellowcake.py")

class ExtractRequest(BaseModel):
    url: HttpUrl

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}

def greenhouse_fallback_jobs(url: str):
    u = urlparse(url)
    if u.netloc not in {"boards.greenhouse.io", "www.boards.greenhouse.io"}:
        return None  # not a greenhouse board URL

    parts = [p for p in u.path.split("/") if p]
    if not parts:
        return None

    board_token = parts[0]  # e.g., "airbnb"
    api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"

    r = requests.get(api_url, timeout=30)
    r.raise_for_status()
    payload = r.json()

    jobs = []
    for j in payload.get("jobs", []):
        jobs.append({
            "title": j.get("title"),
            "company": board_token,
            "location": (j.get("location") or {}).get("name"),
            "posting_date": j.get("updated_at"),
            "apply_url": j.get("absolute_url"),
        })
    return jobs


def run_yellowcake_script(url: str) -> dict:
    if not os.getenv("YELLOWCAKE_API_KEY"):
        raise RuntimeError("YELLOWCAKE_API_KEY not set")

    proc = subprocess.run(
        [sys.executable, SCRIPT_PATH, url],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=180,
    )

    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(msg or f"yellowcake.py failed (exit {proc.returncode})")

    current_event = None
    data_lines = []

    for raw in proc.stdout.splitlines():
        line = raw.strip()

        if line.startswith("event:"):
            current_event = line.split(":", 1)[1].strip()
            data_lines = []
            continue

        if line.startswith("data:"):
            data_lines.append(line.split(":", 1)[1].lstrip())

            # Check for limit-reached event
            if current_event == "limit-reached":
                return {"event": "limit-reached", "message": "\n".join(data_lines)}

            # When the script reaches the "complete" event, Yellowcake sends final JSON in data:
            if current_event == "complete":
                try:
                    return json.loads("\n".join(data_lines))
                except json.JSONDecodeError:
                    pass  # keep accumulating if JSON spans multiple lines

    raise RuntimeError("Could not find/parse 'complete' payload from Yellowcake output")

@app.post("/api/extract")
def api_extract(req: ExtractRequest):
    try:
        gh_jobs = greenhouse_fallback_jobs(str(req.url))
        if gh_jobs is not None:
            return {"jobs": gh_jobs}

        payload = run_yellowcake_script(str(req.url))

        # Check for limit-reached event
        if payload.get("event") == "limit-reached":
            raise HTTPException(
                status_code=429,
                detail="Yellowcake API limit reached. Please try again later or use a Greenhouse URL (e.g., https://boards.greenhouse.io/airbnb)"
            )

        data = payload.get("data")
        if isinstance(data, list):
            jobs = data
        elif isinstance(data, dict) and isinstance(data.get("jobs"), list):
            jobs = data["jobs"]
        else:
            jobs = []

        return {"jobs": jobs}
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))