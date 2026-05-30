"""
game_alert.py
Checks if the Jazz play today. If yes, posts a game day embed to #game-chat.
Uses the free NBA API — no key required.
"""

import requests
import os
from datetime import datetime, timezone

WEBHOOK_URL = os.environ["WEBHOOK_GAME_CHAT"]
JAZZ_TEAM_ID = 1610612762  # Official NBA team ID for Utah Jazz

# Jazz navy and gold
EMBED_COLOR = 0x002B5C  # Navy
GOLD = 0xF9A01B


def get_todays_jazz_game():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url = f"https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json"
    
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        data = res.json()
        game_dates = data["leagueSchedule"]["gameDates"]
        
        for date_entry in game_dates:
            if date_entry["gameDate"].startswith(today):
                for game in date_entry["games"]:
                    home = game["homeTeam"]
                    away = game["awayTeam"]
                    if home["teamId"] == JAZZ_TEAM_ID or away["teamId"] == JAZZ_TEAM_ID:
                        return game, home, away
    except Exception as e:
        print(f"Error fetching schedule: {e}")
    
    return None, None, None


def format_game_time(game):
    """Convert UTC game time to Mountain Time display string."""
    try:
        game_time_utc = game.get("gameDateTimeUTC", "")
        if not game_time_utc:
            return "Check local listings"
        dt = datetime.fromisoformat(game_time_utc.replace("Z", "+00:00"))
        # MT is UTC-6 (MDT) or UTC-7 (MST) — using MDT for Jazz season
        mt_hour = (dt.hour - 6) % 24
        period = "PM" if mt_hour >= 12 else "AM"
        display_hour = mt_hour % 12 or 12
        return f"{display_hour}:{dt.minute:02d} {period} MT"
    except:
        return "Tonight"


def post_game_alert(game, home, away):
    is_home = home["teamId"] == JAZZ_TEAM_ID
    opponent = away if is_home else home
    location = "🏠 Home" if is_home else "✈️ Away"
    game_time = format_game_time(game)
    opponent_name = f"{opponent['teamCity']} {opponent['teamName']}"

    embed = {
        "title": "🏀 GAME DAY — Utah Jazz",
        "description": (
            f"**{location} vs. {opponent_name}**\n"
            f"⏰ Tip-off: **{game_time}**\n\n"
            f"Head to <#game-chat> to watch along and react live!\n"
            f"🎥 Check #announcements for tonight's watch-along details."
        ),
        "color": EMBED_COLOR,
        "footer": {
            "text": "Utah Jazz Discord Bot • Go Jazz! 🎷"
        },
        "thumbnail": {
            "url": "https://cdn.nba.com/logos/nba/1610612762/global/L/logo.svg"
        }
    }

    payload = {
        "username": "Jazz Bot",
        "embeds": [embed]
    }

    r = requests.post(WEBHOOK_URL, json=payload)
    if r.status_code in (200, 204):
        print(f"✅ Game alert posted: Jazz vs {opponent_name} at {game_time}")
    else:
        print(f"❌ Failed to post: {r.status_code} {r.text}")


def main():
    game, home, away = get_todays_jazz_game()
    if game:
        post_game_alert(game, home, away)
    else:
        print("No Jazz game today — skipping alert.")


if __name__ == "__main__":
    main()
