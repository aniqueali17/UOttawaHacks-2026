# auth_server.py
import os, json, time, socket, re
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).with_name(".env"))

import cv2
from google import genai
from google.genai import types
from google.genai import errors

MODEL = "gemini-3-flash-preview"  # you can swap to another flash model if needed
HOST = "0.0.0.0"
PORT = 5000

PROMPT = """
You will receive TWO FACE CROPS: (1) authorized reference, (2) live login.
Decide if they are the SAME PERSON.

Be extremely strict:
- If you are not sure, set match=false.
- Only set match=true if you are highly confident they are the same person.
- Background/lighting should be ignored.

Return ONLY valid JSON:
{ "match": true/false, "confidence": "low"|"medium"|"high", "reason": "..." }
"""


def part_from_path(path: str) -> types.Part:
    with open(path, "rb") as f:
        b = f.read()
    return types.Part.from_bytes(data=b, mime_type="image/jpeg")

def frame_to_part(frame) -> types.Part:
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        raise RuntimeError("Failed to encode frame")
    return types.Part.from_bytes(data=buf.tobytes(), mime_type="image/jpeg")

def generate_with_retry(client, model, contents, max_retries=5):
    for _ in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
        except errors.ClientError as e:
            msg = str(e)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                m = re.search(r"Please retry in ([0-9.]+)s", msg)
                wait_s = float(m.group(1)) if m else 60.0
                print(f"⏳ Rate-limited. Sleeping {wait_s:.1f}s...")
                time.sleep(wait_s + 1)
                continue
            raise
    raise RuntimeError("Too many 429 retries")

def verify_face(client) -> bool:
    if not os.path.exists("authorized.jpg"):
        raise RuntimeError("authorized.jpg not found. Run capture_authorized.py first.")

    cap = cv2.VideoCapture(0)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return False

    authorized = part_from_path("authorized.jpg")
    live = frame_to_part(frame)

    resp = generate_with_retry(
        client,
        model=MODEL,
        contents=[authorized, live, PROMPT],
    )

    data = json.loads(resp.text)

    print("Gemini JSON:", data)

    return (data.get("match") is True) and (data.get("confidence") == "high")

def main():
    # API key from env var GEMINI_API_KEY (same style you used already)
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY missing in environment/.env")

    client = genai.Client()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(5)
    print(f"Auth server listening on {HOST}:{PORT}")

    while True:
        conn, addr = srv.accept()
        try:
            conn.settimeout(10)
            _ = conn.recv(1024)  # read request (can be anything)
            ok = verify_face(client)
            conn.sendall(b"AUTH_SUCCESS\n" if ok else b"AUTH_FAIL\n")
            print(addr, "=>", "AUTH_SUCCESS" if ok else "AUTH_FAIL")
        except Exception as e:
            try:
                conn.sendall(b"AUTH_FAIL\n")
            except:
                pass
            print("Error:", e)
        finally:
            conn.close()

if __name__ == "__main__":
    main()
