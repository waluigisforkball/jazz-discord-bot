# Utah Jazz Discord Bot 🎷

Automated Discord alerts for your Jazz server. No paid APIs. Runs free on GitHub Actions.

## What It Does

| Script | Channel | Schedule |
|---|---|---|
| `game_alert.py` | `#game-chat` | Every day at 9 AM MT |
| `live_score.py` | `#game-chat` | Every 5 min, 6–11 PM MT (game nights) |
| `standings.py` | `#analytics` | Every Monday at 9 AM MT |
| `news_digest.py` | `#team-news` + `#league-news` | Every day at 9 AM MT |

---

## Setup (15–20 minutes)

### Step 1 — Create the GitHub Repo

1. Go to [github.com](https://github.com) and log in
2. Click the **+** icon → **New repository**
3. Name it: `jazz-discord-bot`
4. Set it to **Private**
5. Click **Create repository**

### Step 2 — Upload the Files

You need this exact folder structure in your repo:

```
jazz-discord-bot/
├── .github/
│   └── workflows/
│       └── jazz_bot.yml
└── scripts/
    ├── game_alert.py
    ├── live_score.py
    ├── standings.py
    └── news_digest.py
```

**To upload:**
1. In your new repo, click **Add file → Upload files**
2. Upload all 5 files (the workflow file must go in `.github/workflows/`)

> **Tip for the workflow file:** GitHub can't create nested folders via drag-and-drop easily.
> Instead, click **Create new file**, type `.github/workflows/jazz_bot.yml` as the filename,
> then paste the contents of `jazz_bot.yml` into the editor.

### Step 3 — Create Discord Webhooks

You need **4 webhooks**, one per channel. For each channel:

1. Open your Discord server
2. Right-click the channel → **Edit Channel**
3. Go to **Integrations → Webhooks → New Webhook**
4. Name it `Jazz Bot`
5. Click **Copy Webhook URL**
6. Save it somewhere temporarily (you'll add all 4 to GitHub next)

| Channel | Secret Name to Use |
|---|---|
| `#game-chat` | `WEBHOOK_GAME_CHAT` |
| `#analytics` | `WEBHOOK_ANALYTICS` |
| `#team-news` | `WEBHOOK_TEAM_NEWS` |
| `#league-news` | `WEBHOOK_LEAGUE_NEWS` |

### Step 4 — Add Secrets to GitHub

1. In your GitHub repo, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** for each webhook:
   - Name: `WEBHOOK_GAME_CHAT` → paste the `#game-chat` webhook URL
   - Name: `WEBHOOK_ANALYTICS` → paste the `#analytics` webhook URL
   - Name: `WEBHOOK_TEAM_NEWS` → paste the `#team-news` webhook URL
   - Name: `WEBHOOK_LEAGUE_NEWS` → paste the `#league-news` webhook URL

### Step 5 — Test It

1. Go to your repo → **Actions** tab
2. Click **Jazz Discord Bot** in the left sidebar
3. Click **Run workflow → Run workflow**
4. Watch it run — check your Discord channels for posts

---

## Troubleshooting

**Nothing posted to Discord**
- Double-check your webhook URLs in GitHub Secrets (no trailing spaces)
- Make sure the webhook is for the right channel

**"No Jazz game today" even on game days**
- The NBA schedule API occasionally updates slowly — it will self-correct

**Actions tab shows red X**
- Click the failed run → click the failed job → read the error log
- Most common cause: a typo in a secret name

---

## Notes

- All times are Mountain Time (MT)
- The live score updater only runs 6–11 PM MT to save GitHub Actions minutes
- Reddit RSS requires no login or API key — it's completely public
- The bot uses the unofficial NBA CDN API which is free and reliable during the season

