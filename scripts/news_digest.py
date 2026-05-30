"""
news_digest.py
Daily/weekly digest from r/UtahJazz and r/nba.

Schedule logic (handled here, not in the workflow):
  In-season (Oct 1 – Jun 30):
    - #team-news: daily Mon–Fri
    - #league-news: Mon/Wed/Fri only
  Offseason (Jul 1 – Sep 30):
    - Both channels: Mondays only

The CRON_TRIGGER env var tells us which cron fired.
On manual runs, both channels always post.
"""

import feedparser
import requests
import os
from datetime import datetime, timezone

WEBHOOK_TEAM_NEWS = os.environ["WEBHOOK_TEAM_NEWS"]
WEBHOOK_LEAGUE_NEWS = os.environ["WEBHOOK_LEAGUE_NEWS"]
EMBED_COLOR_JAZZ = 0x002B5C
EMBED_COLOR_LEAGUE = 0x1A1A2E

MAX_POSTS = 5

# Cron strings from the workflow
CRON_DAILY_WEEKDAY = '0 16 * * 1-5'      # team news trigger (in-season)
CRON_MWF = '0 16 * * 1,3,5'              # league news trigger (in-season)
# Offseason: both share the Monday cron '0 16 * * 1'


def is_nba_season():
    """Oct 1 – Jun 30 is considered in-season."""
    month = datetime.now(timezone.utc).month
    return month >= 10 or month <= 6


def should_post_team_news(cron_trigger, manual):
    if manual:
        return True
    if is_nba_season():
        # Daily weekday cron fires this
        return cron_trigger == CRON_DAILY_WEEKDAY
    else:
        # Offseason: Monday cron only
        return cron_trigger == '0 16 * * 1'


def should_post_league_news(cron_trigger, manual):
    if manual:
        return True
    if is_nba_season():
        # Mon/Wed/Fri cron fires this
        return cron_trigger == CRON_MWF
    else:
        # Offseason: Monday cron only
        return cron_trigger == '0 16 * * 1'


def fetch_reddit_rss(subreddit, limit=MAX_POSTS):
    url = f"https://www.reddit.com/r/{subreddit}/hot.rss?limit={limit + 5}"
    try:
        feed = feedparser.parse(url)
        posts = []
        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            if title and link and not title.lower().startswith("r/"):
                posts.append({"title": title, "url": link})
            if len(posts) >= limit:
                break
        return posts
    except Exception as e:
        print(f"Error fetching r/{subreddit}: {e}")
        return []


def build_digest_embed(posts, title, description_header, color, footer):
    if not posts:
        return None
    lines = []
    for i, post in enumerate(posts, 1):
        t = post["title"]
        if len(t) > 80:
            t = t[:77] + "..."
        lines.append(f"{i}. [{t}]({post['url']})")

    embed = {
        "title": title,
        "description": f"{description_header}\n\n" + "\n".join(lines),
        "color": color,
        "footer": {"text": footer},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return embed


def post_to_webhook(webhook_url, embed):
    payload = {"username": "Jazz Bot", "embeds": [embed]}
    r = requests.post(webhook_url, json=payload)
    if r.status_code in (200, 204):
        print("✅ Posted successfully")
    else:
        print(f"❌ Failed: {r.status_code} {r.text}")


def main():
    cron_trigger = os.environ.get("CRON_TRIGGER", "")
    manual = cron_trigger == ""
    today = datetime.now(timezone.utc).strftime("%A, %B %d")
    season_label = "In-Season" if is_nba_season() else "Offseason"

    print(f"Mode: {'Manual' if manual else 'Scheduled'} | {season_label} | Cron: '{cron_trigger}'")

    # --- Team news → #team-news ---
    if should_post_team_news(cron_trigger, manual):
        posts = fetch_reddit_rss("UtahJazz")
        if posts:
            embed = build_digest_embed(
                posts=posts,
                title=f"🎷 Jazz Daily Digest — {today}",
                description_header="Top posts from r/UtahJazz today:",
                color=EMBED_COLOR_JAZZ,
                footer="Utah Jazz Discord Bot • Source: r/UtahJazz"
            )
            if embed:
                post_to_webhook(WEBHOOK_TEAM_NEWS, embed)
    else:
        print("Skipping #team-news — not scheduled for today.")

    # --- League news → #league-news ---
    if should_post_league_news(cron_trigger, manual):
        posts = fetch_reddit_rss("nba")
        if posts:
            embed = build_digest_embed(
                posts=posts,
                title=f"🏀 NBA League Digest — {today}",
                description_header="What's trending across the league on r/nba:",
                color=EMBED_COLOR_LEAGUE,
                footer="Utah Jazz Discord Bot • Source: r/nba"
            )
            if embed:
                post_to_webhook(WEBHOOK_LEAGUE_NEWS, embed)
    else:
        print("Skipping #league-news — not scheduled for today.")


if __name__ == "__main__":
    main()
