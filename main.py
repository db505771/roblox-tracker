<details>
<summary>📂 Click to reveal full <code>main.py</code></summary>
import requests
import time
from datetime import datetime

# ✅ Track this Roblox user only
usernames = ["maddiefatty36"]

# Discord webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1320856848135622666/1ctIcem6Epvad8LDEuvOJ_Z_TzaNKn-pjMJBqatVLhYZnHEA04bxxx24PKXDXHT1oCLo"

# Toggl Track API token
TOGGL_API_TOKEN = "a3c0cdd1d52789878c1ac90267e3825d"

def get_user_ids(usernames):
    user_ids = []
    for name in usernames:
        url = f"https://api.roblox.com/users/get-by-username?username={name}"
        r = requests.get(url).json()
        if "Id" in r:
            user_ids.append((name, r["Id"]))
    return user_ids

def check_presence(user_ids):
    ids = [uid for _, uid in user_ids]
    url = "https://presence.roblox.com/v1/presence/users"
    res = requests.post(url, json={"userIds": ids})
    return res.json()["userPresences"]

def send_discord_message(duration):
    message = f"{duration}"
    payload = {"content": message}
    requests.post(WEBHOOK_URL, json=payload)

def start_toggl_entry(username):
    url = "https://api.track.toggl.com/api/v9/time_entries"
    now = datetime.utcnow().isoformat() + "Z"

    data = {
        "description": f"{username} - Roblox",
        "start": now,
        "created_with": "roblox-tracker",
        "tags": ["Roblox"]
    }

    r = requests.post(url, auth=(TOGGL_API_TOKEN, "api_token"), json=data)
    if r.ok:
        return r.json()["id"]
    else:
        print(f"Toggl start failed: {r.text}")
        return None

def stop_toggl_entry(entry_id):
    url = f"https://api.track.toggl.com/api/v9/time_entries/{entry_id}/stop"
    r = requests.patch(url, auth=(TOGGL_API_TOKEN, "api_token"))
    if not r.ok:
        print(f"Toggl stop failed: {r.text}")

def track():
    user_ids = get_user_ids(usernames)
    sessions = {}

    while True:
        presence = check_presence(user_ids)
        now = datetime.utcnow()

        for p in presence:
            name = [n for n, uid in user_ids if uid == p["userId"]][0]
            status = p["userPresenceType"]
            in_game = status == 2

            if in_game:
                if name not in sessions:
                    # Start new session
                    entry_id = start_toggl_entry(name)
                    sessions[name] = {"start": now, "toggl_id": entry_id}
                    print(f"[{now}] {name} started playing")

            else:
                if name in sessions:
                    # End session
                    start_time = sessions[name]["start"]
                    duration = (now - start_time).seconds // 60
                    print(f"[{now}] {name} stopped. Duration: {duration} minutes")

                    send_discord_message(duration)
                    if sessions[name]["toggl_id"]:
                        stop_toggl_entry(sessions[name]["toggl_id"])

                    del sessions[name]

        time.sleep(60)

if __name__ == "__main__":
    track()
  </details>
