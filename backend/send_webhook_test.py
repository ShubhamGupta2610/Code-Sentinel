import hmac, hashlib
import requests
from pathlib import Path

secret = b"devsecret"  # must match .env
body = Path("sample_webhook.json").read_bytes()
expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

resp = requests.post(
    "http://127.0.0.1:8000/webhook",
    headers={"Content-Type": "application/json", "X-Hub-Signature-256": expected},
    data=body,
)
print("sig:", expected)
print(resp.status_code, resp.text)
