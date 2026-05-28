import hashlib
import hmac
import json
import os
import urllib.request
from datetime import datetime, timezone


def required_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


payload = {
    "action_run_link": required_env("B12_ACTION_RUN_LINK"),
    "email": required_env("B12_EMAIL"),
    "name": required_env("B12_NAME"),
    "repository_link": required_env("B12_REPOSITORY_LINK"),
    "resume_link": required_env("B12_RESUME_LINK"),
    "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
}
body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
signature = hmac.new(required_env("B12_SIGNING_SECRET").encode("utf-8"), body, hashlib.sha256).hexdigest()
request = urllib.request.Request(
    "https://b12.io/apply/submission",
    data=body,
    headers={"Content-Type": "application/json", "X-Signature-256": f"sha256={signature}"},
    method="POST",
)

with urllib.request.urlopen(request, timeout=30) as response:
    result = json.loads(response.read().decode("utf-8"))
    if not result.get("success"):
        raise RuntimeError(f"Submission failed: {result}")
    print(result["receipt"])
