# 🔓 Save Restricted Bot

Telegram bot to save content from restricted channels using Pyrogram userbot.

## Features
- Save photos, videos, documents, audio from restricted channels
- High-speed MTProto protocol (Pyrogram)
- Works on private and public restricted channels

## Setup

### Step 1: Get Credentials
1. Go to https://my.telegram.org
2. Login → API Development Tools
3. Create new app → Copy `api_id` and `api_hash`
4. Get bot token from @BotFather

### Step 2: Generate Session String
Run locally once:
```bash
pip install pyrogram TgCrypto
python generate_session.py
```
Copy the session string output.

### Step 3: Deploy on Koyeb

1. Push this repo to GitHub
2. Go to koyeb.com → New App → GitHub
3. Add these Environment Variables:
   - `API_ID` — your api_id
   - `API_HASH` — your api_hash
   - `BOT_TOKEN` — your bot token
   - `SESSION_STRING` — generated session string
4. Start command: `python bot.py`

## Environment Variables

| Variable | Description |
|----------|-------------|
| `API_ID` | From my.telegram.org |
| `API_HASH` | From my.telegram.org |
| `BOT_TOKEN` | From @BotFather |
| `SESSION_STRING` | From generate_session.py |

## Usage

Send any `t.me` link to the bot:
- `https://t.me/channelname/123`
- `https://t.me/c/1234567890/123`

⚠️ Make sure the userbot account has joined the source channel!
