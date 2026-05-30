"""
news_digest.py
Daily digest pulling from:
- r/UtahJazz RSS feed (top posts) → #team-news
- r/nba RSS (league-wide) → #league-news
No API keys required. Uses feedparser for RSS.
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
            # Filter out stickied mod posts and low-effort titles
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
        # Truncate long titles
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
    payload = {
        "username": "Jazz Bot",
        "embeds": [embed]
    }
    r = requests.post(webhook_url, json=payload)
    if r.status_code in (200, 204):
        print(f"✅ Posted to webhook")
    else:
        print(f"❌ Failed: {r.status_code} {r.text}")


def main():
    today = datetime.now(timezone.utc).strftime("%A, %B %d")

    # --- Jazz news → #team-news ---
    jazz_posts = fetch_reddit_rss("UtahJazz")
    if jazz_posts:
        embed = build_digest_embed(
            posts=jazz_posts,
            title=f"🎷 Jazz Daily Digest — {today}",
            description_header="Top posts from r/UtahJazz today:",
            color=EMBED_COLOR_JAZZ,
            footer="Utah Jazz Discord Bot • Source: r/UtahJazz"
        )
        if embed:
            post_to_webhook(WEBHOOK_TEAM_NEWS, embed)
    else:
        print("No Jazz posts found.")

    # --- League news → #league-news ---
    nba_posts = fetch_reddit_rss("nba")
    if nba_posts:
        embed = build_digest_embed(
            posts=nba_posts,
            title=f"🏀 NBA League Digest — {today}",
            description_header="What's trending across the league on r/nba:",
            color=EMBED_COLOR_LEAGUE,
            footer="Utah Jazz Discord Bot • Source: r/nba"
        )
        if embed:
            post_to_webhook(WEBHOOK_LEAGUE_NEWS, embed)
    else:
        print("No NBA posts found.")


if __name__ == "__main__":
    main()
