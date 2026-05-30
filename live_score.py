"""
live_score.py
Runs every 5 minutes during game windows (6–11 PM MT).
Posts a score update if Jazz are playing. Edits the existing message each quarter
so the channel stays clean. Posts a final recap when the game ends.

Uses GitHub Actions artifacts to persist the message ID between runs.
"""

import requests
import os
import json
from datetime import datetime, timezone

WEBHOOK_URL = os.environ["WEBHOOK_GAME_CHAT"]
JAZZ_TEAM_ID = 1610612762
EMBED_COLOR_LIVE = 0xF9A01B   # Gold while live
EMBED_COLOR_FINAL = 0x002B5C  # Navy for final


def get_live_jazz_game():
    """Check NBA scoreboard for a live or recent Jazz game."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
    
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        data = res.json()
        games = data["scoreboard"]["games"]
        
        for game in games:
            home = game["homeTeam"]
            away = game["awayTeam"]
            if home["teamId"] == JAZZ_TEAM_ID or away["teamId"] == JAZZ_TEAM_ID:
                return game
    except Exception as e:
        print(f"Error fetching scoreboard: {e}")
    
    return None


def build_score_embed(game):
    home = game["homeTeam"]
    away = game["awayTeam"]
    status = game["gameStatusText"]  # e.g. "Q3 4:22", "Final", "Halftime"
    game_status = game["gameStatus"]  # 1=scheduled, 2=live, 3=final

    is_jazz_home = home["teamId"] == JAZZ_TEAM_ID
    jazz = home if is_jazz_home else away
    opp = away if is_jazz_home else home

    jazz_score = jazz["score"]
    opp_score = opp["score"]
    opp_name = f"{opp['teamCity']} {opp['teamName']}"

    winning = int(jazz_score) > int(opp_score) if jazz_score and opp_score else False
    tied = jazz_score == opp_score

    if game_status == 3:
        # Final
        result = "✅ WIN" if winning else ("🤝 TIE" if tied else "❌ LOSS")
        title = f"🏁 FINAL — Utah Jazz {result}"
        color = EMBED_COLOR_FINAL
        desc = (
            f"**Utah Jazz {jazz_score} — {opp_score} {opp_name}**\n\n"
            f"Head to <#post-game-reactions> to share your thoughts!\n"
        )
    elif game_status == 2:
        # Live
        lead = "🔥 Leading" if winning else ("⚖️ Tied" if tied else "📉 Trailing")
        title = f"🔴 LIVE — Utah Jazz • {status}"
        color = EMBED_COLOR_LIVE
        desc = (
            f"**Utah Jazz {jazz_score} — {opp_score} {opp_name}**\n"
            f"{lead} • {status}\n\n"
            f"_Score updates every 5 minutes_"
        )
    else:
        return None, None

    embed = {
        "title": title,
        "description": desc,
        "color": color,
        "footer": {"text": "Utah Jazz Discord Bot • Data via NBA.com"}
    }

    return embed, game_status


def load_message_id():
    """Load persisted webhook message ID from file (written by previous run)."""
    try:
        with open("/tmp/jazz_score_msg_id.txt", "r") as f:
            return f.read().strip()
    except:
        return None


def save_message_id(msg_id):
    with open("/tmp/jazz_score_msg_id.txt", "w") as f:
        f.write(str(msg_id))


def post_or_edit_score(embed, game_status):
    """Post new message, or edit existing one. Delete stored ID on Final."""
    msg_id = load_message_id()

    if msg_id and game_status == 2:
        # Edit existing live message
        edit_url = f"{WEBHOOK_URL}/messages/{msg_id}"
        r = requests.patch(edit_url, json={"embeds": [embed]})
        if r.status_code == 200:
            print(f"✅ Score updated (edit) — msg {msg_id}")
        else:
            print(f"⚠️ Edit failed ({r.status_code}), posting new message")
            post_new(embed, game_status)
    else:
        post_new(embed, game_status)


def post_new(embed, game_status):
    r = requests.post(WEBHOOK_URL + "?wait=true", json={
        "username": "Jazz Bot",
        "embeds": [embed]
    })
    if r.status_code == 200:
        data = r.json()
        msg_id = data.get("id")
        if game_status == 2:
            save_message_id(msg_id)
            print(f"✅ New score post created — msg {msg_id}")
        else:
            # Final — clear stored ID so next game starts fresh
            try:
                os.remove("/tmp/jazz_score_msg_id.txt")
            except:
                pass
            print("✅ Final recap posted — message ID cleared")
    else:
        print(f"❌ Post failed: {r.status_code} {r.text}")


def main():
    game = get_live_jazz_game()
    if not game:
        print("No Jazz game active right now.")
        return

    embed, game_status = build_score_embed(game)
    if embed:
        post_or_edit_score(embed, game_status)
    else:
        print("Game scheduled but not started yet.")


if __name__ == "__main__":
    main()
