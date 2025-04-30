# Maznet Config Scraper

This script monitors a Telegram channel for VLESS configurations and makes them available through a Cloudflare Worker.

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
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

4. Add the following environment variables in Railway dashboard:
   - `TELEGRAM_API_ID`
   - `TELEGRAM_API_HASH`
   - `CF_API_TOKEN`
   - `CF_ACCOUNT_ID`
   - `CF_KV_NAMESPACE_ID`

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