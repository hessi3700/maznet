# Maznet Config Scraper

This script monitors a Telegram channel for VLESS configurations and makes them available through a Cloudflare Worker.

## Required Environment Variables

The following environment variables must be set in Railway:

- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API Hash
- `CHANNEL_USERNAME`: The Telegram channel username to monitor (defaults to 'Maznet')
- `CF_API_TOKEN`: Your Cloudflare API token
- `CF_ACCOUNT_ID`: Your Cloudflare account ID
- `CF_KV_NAMESPACE_ID`: Your Cloudflare KV namespace ID

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with all required credentials:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
CHANNEL_USERNAME=your_channel_username
CF_API_TOKEN=your_cloudflare_token
CF_ACCOUNT_ID=your_cloudflare_account_id
CF_KV_NAMESPACE_ID=your_kv_namespace_id
```

3. Run the script:
```bash
python3 telegram_channel_scraper.py
```

## Deployment to Railway.app

1. Create an account on [Railway.app](https://railway.app)

2. Create a new project and select "Deploy from GitHub repository"

3. Connect your GitHub repository

4. Add all required environment variables in Railway dashboard

5. Railway will automatically deploy your app

## Usage

The latest VLESS config is always available at:
```
https://maznet-configs.hessi3700.workers.dev/
```

## Features

- Monitors Telegram channel for new VLESS configs
- Automatically syncs configs to Cloudflare KV storage
- Provides latest config through Cloudflare Worker
- Runs 24/7 when deployed to Railway
- Resets and updates KV storage on startup 
