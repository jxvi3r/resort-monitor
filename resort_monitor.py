import requests
import json
import os
from pathlib import Path

API_URL = "https://my.smallerearth.com/api/v1/participants/application_containers/1110115/employers?page=1"

HEADERS = {
"X-Api-Key": os.getenv("X_API_KEY"),
"X-Auth-Token": os.getenv("X_AUTH_TOKEN")
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STATE_FILE = "known_resorts.json"

def send_telegram(message):
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

```
requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    },
    timeout=30
)
```

def get_open_resorts():
r = requests.get(
API_URL,
headers=HEADERS,
timeout=30
)

```
r.raise_for_status()

data = r.json()

resorts = []

for employer in data["employers"]:
    if employer.get("interviews_available"):
        resorts.append({
            "name": employer["name"],
            "location": employer["location"]
        })

return resorts
```

def load_known():
if not Path(STATE_FILE).exists():
return []

```
with open(STATE_FILE, "r", encoding="utf-8") as f:
    return json.load(f)
```

def save_known(data):
with open(STATE_FILE, "w", encoding="utf-8") as f:
json.dump(data, f)

known = load_known()
current = get_open_resorts()

known_names = {r["name"] for r in known}
current_names = {r["name"] for r in current}

new_resorts = current_names - known_names

for resort in current:
if resort["name"] in new_resorts:

```
    msg = (
        "🚨 NUEVA ENTREVISTA DISPONIBLE\n\n"
        f"🏨 {resort['name']}\n"
        f"📍 {resort['location']}"
    )

    send_telegram(msg)
```

save_known(current)
print("Proceso completado.")
