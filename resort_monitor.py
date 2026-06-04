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

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )


def get_open_resorts():

    resorts = []

    for page in [1, 2]:

        r = requests.get(
            f"https://my.smallerearth.com/api/v1/participants/application_containers/1110115/employers?page={page}",
            headers=HEADERS,
            timeout=30
        )

        r.raise_for_status()

        data = r.json()

        for employer in data["employers"]:

            roles = []

            for skill in employer.get("skills", []):
                roles.append(skill["name"])

            resorts.append({
                "name": employer["name"],
                "location": employer["location"],
                "roles": roles,
                "interviews_available": employer.get("interviews_available", False)
            })

    return resorts


def load_known():
    if not Path(STATE_FILE).exists():
        return []

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_known(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

known = load_known()

try:
    current = get_open_resorts()
except Exception as e:
    print("API no disponible:", e)
    exit(0)

for resort in current:

    previous = next(
        (r for r in known if r["name"] == resort["name"]),
        None
    )

    if previous is None:
        continue

    old_roles = set(previous.get("roles", []))
    new_roles = set(resort.get("roles", []))

    added_roles = new_roles - old_roles

    if added_roles:

        msg = (
            f"🆕 NUEVO PUESTO EN {resort['name']}\n\n"
            + "\n".join(f"• {role}" for role in added_roles)
        )

        send_telegram(msg)

    if (
        not previous.get("interviews_available", False)
        and resort.get("interviews_available", False)
    ):

        msg = (
            "🚨 ENTREVISTA ABIERTA\n\n"
            f"🏨 {resort['name']}\n"
            f"📍 {resort['location']}"
        )

        send_telegram(msg)

save_known(current)

print("Proceso completado.")
