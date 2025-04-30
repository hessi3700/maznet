# Maznet Config Scraper

This script monitors a Telegram channel for VLESS configurations and makes them available through a Cloudflare Worker.

## Required Environment Variables

The following environment variables must be set in Railway:

- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API Hash
- `CHANNEL_USERNAME`: The Telegram channel username to monitor (defaults to 'paznethessi')
- `CF_API_TOKEN`: Your Cloudflare API token
- `CF_ACCOUNT_ID`: Your Cloudflare account ID
- `CF_KV_NAMESPACE_ID`: Your Cloudflare KV namespace ID

## Cloudflare Setup

1. **Create a Cloudflare Account**:
   - Sign up at [Cloudflare](https://www.cloudflare.com/)
   - Add your domain to Cloudflare

2. **Create a KV Namespace**:
   - Go to Workers & Pages → KV
   - Click "Create a namespace"
   - Name it "maznet-configs"
   - Copy the namespace ID (you'll need this for `CF_KV_NAMESPACE_ID`)

3. **Create a Cloudflare API Token**:
   - Go to My Profile → API Tokens
   - Click "Create Token"
   - Select "Create Custom Token"
   - Add the following permissions:
     - Workers KV: Edit
     - Account: Workers Scripts: Edit
   - Set the token name to "maznet-configs"
   - Copy the token (you'll need this for `CF_API_TOKEN`)

4. **Create a Cloudflare Worker**:
   - Go to Workers & Pages → Create application
   - Choose "Create Worker"
   - Name it "maznet-configs"
   - Copy the following code into the worker:

```javascript
export default {
  async fetch(request, env) {
    const config = await env.MAZNET_CONFIGS.get('latest_configs');
    if (!config) {
      return new Response('No configurations available', { status: 404 });
    }
    
    return new Response(config, {
      headers: {
        'content-type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
};
```

5. **Bind KV to Worker**:
   - In your worker settings, go to "Settings" → "Variables"
   - Under "KV Namespace Bindings", click "Add binding"
   - Set the variable name to "MAZNET_CONFIGS"
   - Select your KV namespace
   - Click "Save"

6. **Get Your Account ID**:
   - Go to Workers & Pages
   - Your Account ID is shown in the URL or in the right sidebar
   - Copy this ID (you'll need this for `CF_ACCOUNT_ID`)

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
https://maznet-configs.your-worker-name.workers.dev/
```

## Features

- Monitors Telegram channel for new VLESS configs
- Automatically syncs configs to Cloudflare KV storage
- Provides latest config through Cloudflare Worker
- Runs 24/7 when deployed to Railway
- Resets and updates KV storage on startup
