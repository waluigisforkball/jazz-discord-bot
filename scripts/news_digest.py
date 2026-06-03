"""
news_digest.py
Weekly Monday digest from r/UtahJazz and r/nba.
Posts to #team-news and #league-news every Monday at 9 AM MT.
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


def build_embed(posts, title, header, color, footer):
    if not posts:
        return None
    lines = []
    for i, post in enumerate(posts, 1):
        t = post["title"][:77] + "..." if len(post["title"]) > 80 else post["title"]
        lines.append(f"{i}. [{t}]({post['url']})")
    return {
        "title": title,
        "description": f"{header}\n\n" + "\n".join(lines),
        "color": color,
        "footer": {"text": footer},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def post_to_webhook(webhook_url, embed):
    r = requests.post(webhook_url, json={"username": "Jazz Bot", "embeds": [embed]})
    if r.status_code in (200, 204):
        print("✅ Posted successfully")
    else:
        print(f"❌ Failed: {r.status_code} {r.text}")


def main():
    today = datetime.now(timezone.utc).strftime("%A, %B %d")

    # Jazz news → #team-news
    jazz_posts = fetch_reddit_rss("UtahJazz")
    if jazz_posts:
        embed = build_embed(jazz_posts, f"🎷 Jazz Weekly Digest — {today}",
            "Top posts from r/UtahJazz this week:", EMBED_COLOR_JAZZ,
            "Utah Jazz Discord Bot • Every Monday • Source: r/UtahJazz")
        if embed:
            post_to_webhook(WEBHOOK_TEAM_NEWS, embed)

    # League news → #league-news
    nba_posts = fetch_reddit_rss("nba")
    if nba_posts:
        embed = build_embed(nba_posts, f"🏀 NBA Weekly Digest — {today}",
            "What's trending across the league on r/nba:", EMBED_COLOR_LEAGUE,
            "Utah Jazz Discord Bot • Every Monday • Source: r/nba")
        if embed:
            post_to_webhook(WEBHOOK_LEAGUE_NEWS, embed)


if __name__ == "__main__":
    main()
