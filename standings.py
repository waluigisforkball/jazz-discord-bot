"""
standings.py
Posts Western Conference standings every Monday morning to #analytics.
Free NBA API, no key required.
"""

import requests
import os

WEBHOOK_URL = os.environ["WEBHOOK_ANALYTICS"]
JAZZ_TEAM_ID = 1610612762
EMBED_COLOR = 0x002B5C


def get_standings():
    url = "https://cdn.nba.com/static/json/staticData/seasonSummary.json"
    
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        data = res.json()
        # Try the live standings endpoint instead
    except:
        pass

    # Primary: live standings endpoint
    url = "https://cdn.nba.com/static/json/liveData/standings/standings_00.json"
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        data = res.json()
        standings = data["standings"]["teams"]
        
        west = [t for t in standings if t["conference"] == "West"]
        west.sort(key=lambda x: (int(x["losses"]), -int(x["wins"])))
        return west
    except Exception as e:
        print(f"Error fetching standings: {e}")
        return []


def format_standings(west_teams):
    lines = []
    jazz_pos = None

    for i, team in enumerate(west_teams[:15], 1):
        name = f"{team['teamCity']} {team['teamName']}"
        w = team["wins"]
        l = team["losses"]
        pct = team["winPct"]
        gb = team["gamesBehind"] if team["gamesBehind"] != "0" else "—"

        is_jazz = team["teamId"] == JAZZ_TEAM_ID
        if is_jazz:
            jazz_pos = i
            line = f"**{i}. {name} ({w}-{l}, {pct}) GB: {gb} ← 🎷**"
        else:
            line = f"{i}. {name} ({w}-{l}, {pct}) GB: {gb}"
        lines.append(line)

    return "\n".join(lines), jazz_pos


def post_standings(west_teams):
    table, jazz_pos = format_standings(west_teams)

    seed_desc = ""
    if jazz_pos:
        if jazz_pos <= 6:
            seed_desc = f"✅ Playoff seed #{jazz_pos}"
        elif jazz_pos <= 10:
            seed_desc = f"🎯 Play-In position #{jazz_pos}"
        else:
            seed_desc = f"📉 Outside playoff picture (#{jazz_pos})"

    embed = {
        "title": "📊 Western Conference Standings",
        "description": f"{seed_desc}\n\n{table}",
        "color": EMBED_COLOR,
        "footer": {"text": "Utah Jazz Discord Bot • Updated every Monday • Data via NBA.com"}
    }

    payload = {
        "username": "Jazz Bot",
        "embeds": [embed]
    }

    r = requests.post(WEBHOOK_URL, json=payload)
    if r.status_code in (200, 204):
        print("✅ Standings posted")
    else:
        print(f"❌ Failed: {r.status_code} {r.text}")


def main():
    teams = get_standings()
    if teams:
        post_standings(teams)
    else:
        print("Could not fetch standings.")


if __name__ == "__main__":
    main()
