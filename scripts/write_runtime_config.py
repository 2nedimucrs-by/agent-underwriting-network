from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "site" / "runtime-config.js"

supabase_url = os.environ.get("AUN_SUPABASE_URL", "").strip()
supabase_key = os.environ.get("AUN_SUPABASE_ANON_KEY", "").strip()
cloudflare_token = os.environ.get(
    "AUN_CLOUDFLARE_WEB_ANALYTICS_TOKEN",
    "",
).strip()

payload = {
    "authEnabled": bool(supabase_url and supabase_key),
    "productAnalyticsEnabled": bool(supabase_url and supabase_key),
    "supabaseUrl": supabase_url,
    "supabaseAnonKey": supabase_key,
    "cloudflareWebAnalyticsToken": cloudflare_token,
}

OUTPUT.write_text(
    "window.AUN_CONFIG = Object.freeze("
    + json.dumps(payload, separators=(",", ":"))
    + ");\n",
    encoding="utf-8",
)

print(
    "runtime config: "
    f"auth={'ON' if payload['authEnabled'] else 'OFF'} "
    f"product_analytics={'ON' if payload['productAnalyticsEnabled'] else 'OFF'} "
    f"cloudflare={'ON' if bool(cloudflare_token) else 'OFF'}"
)
