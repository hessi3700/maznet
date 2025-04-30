from telethon import TelegramClient, events
from telethon.tl.types import Channel
import json
import asyncio
import os
from datetime import datetime
import re
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your Telegram API credentials
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')

# Channel username or ID to monitor
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', 'Maznet')

# Files to save messages
OUTPUT_FILE = 'channel_messages.json'
CONFIGS_FILE = 'vless_configs.json'

# Cloudflare Worker configuration
CF_API_TOKEN = os.getenv('CF_API_TOKEN')
CF_ACCOUNT_ID = os.getenv('CF_ACCOUNT_ID')
CF_KV_NAMESPACE_ID = os.getenv('CF_KV_NAMESPACE_ID')

# Validate required environment variables
required_vars = {
    'TELEGRAM_API_ID': API_ID,
    'TELEGRAM_API_HASH': API_HASH,
    'CF_API_TOKEN': CF_API_TOKEN,
    'CF_ACCOUNT_ID': CF_ACCOUNT_ID,
    'CF_KV_NAMESPACE_ID': CF_KV_NAMESPACE_ID
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

class TelegramChannelScraper:
    def __init__(self, api_id, api_hash):
        self.client = TelegramClient('channel_scraper_session', api_id, api_hash)
        self.messages = []
        self.configs = []
        self.load_existing_configs()
        self.session = None

    def load_existing_configs(self):
        try:
            if os.path.exists(CONFIGS_FILE):
                with open(CONFIGS_FILE, 'r', encoding='utf-8') as f:
                    self.configs = json.load(f)
        except Exception as e:
            print(f"Error loading existing configs: {e}")

    async def initialize_kv(self):
        """Initialize KV storage with the latest config from channel"""
        try:
            url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/latest_configs"
            headers = {
                "Authorization": f"Bearer {CF_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Get the channel entity
            channel = await self.client.get_entity(CHANNEL_USERNAME)
            
            # Get the last 100 messages
            messages = await self.client.get_messages(channel, limit=100)
            
            # Extract all VLESS configs from messages
            all_configs = []
            for message in messages:
                if message.text:
                    vless_configs = self.extract_vless_config(message.text)
                    if vless_configs:
                        for config in vless_configs:
                            if config not in [c['config'] for c in all_configs]:
                                config_data = {
                                    'config': config,
                                    'date': message.date.isoformat(),
                                    'message_id': message.id
                                }
                                all_configs.append(config_data)
            
            # Sort configs by date (newest first)
            all_configs.sort(key=lambda x: x['date'], reverse=True)
            
            # Update self.configs
            self.configs = all_configs
            
            # Save to KV
            data = {
                "value": json.dumps(self.configs)
            }
            
            async with self.session.put(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print(f"Successfully initialized KV with {len(self.configs)} configs")
                    if self.configs:
                        print(f"Latest config: {self.configs[0]['config']}")
                else:
                    print(f"Failed to initialize KV: {response.status}")
                    print(await response.text())
        except Exception as e:
            print(f"Error initializing KV: {e}")
            import traceback
            print(traceback.format_exc())

    async def connect(self):
        await self.client.start()
        self.session = aiohttp.ClientSession()
        print("Connected to Telegram!")
        # Initialize KV storage with latest configs
        await self.initialize_kv()

    def extract_vless_config(self, text):
        # Pattern to match VLESS configurations, including those in code blocks
        vless_pattern = r'vless://[^\s`]+'
        matches = re.findall(vless_pattern, text)
        return matches

    async def sync_with_cloudflare(self):
        if not self.session:
            return

        try:
            url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/latest_configs"
            headers = {
                "Authorization": f"Bearer {CF_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Print debug info
            print(f"Syncing {len(self.configs)} configs to Cloudflare...")
            print(f"Latest config: {self.configs[-1]['config'] if self.configs else 'None'}")
            
            # Ensure the data is properly formatted
            data = {
                "value": json.dumps(self.configs)
            }
            
            async with self.session.put(url, headers=headers, json=data) as response:
                response_text = await response.text()
                if response.status == 200:
                    print("Successfully synced with Cloudflare")
                    print(f"Current configs count: {len(self.configs)}")
                    print(f"Response: {response_text}")
                else:
                    print(f"Failed to sync with Cloudflare: {response.status}")
                    print(f"Response: {response_text}")
        except Exception as e:
            print(f"Error syncing with Cloudflare: {e}")
            import traceback
            print(traceback.format_exc())

    def save_configs(self):
        try:
            with open(CONFIGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.configs, f, ensure_ascii=False, indent=4)
            print(f"Configs saved to {CONFIGS_FILE}")
            
            # Sync with Cloudflare
            asyncio.create_task(self.sync_with_cloudflare())
        except Exception as e:
            print(f"Error saving configs: {e}")

    async def handle_new_message(self, event):
        try:
            message = event.message
            if message.text:
                # Extract VLESS configs from the message
                vless_configs = self.extract_vless_config(message.text)
                
                if vless_configs:
                    for config in vless_configs:
                        if config not in [c['config'] for c in self.configs]:
                            config_data = {
                                'config': config,
                                'date': message.date.isoformat(),
                                'message_id': message.id
                            }
                            self.configs.append(config_data)
                            print(f"New VLESS config found: {config}")
                            self.save_configs()
                
                # Save the full message
                message_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'text': message.text,
                    'views': message.views if hasattr(message, 'views') else None,
                    'forwards': message.forwards if hasattr(message, 'forwards') else None
                }
                self.messages.append(message_data)
                
                # Save all messages
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.messages, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error handling message: {e}")
            import traceback
            print(traceback.format_exc())

    async def start_monitoring(self):
        # Get the channel entity
        channel = await self.client.get_entity(CHANNEL_USERNAME)
        
        # Set up the event handler for new messages
        @self.client.on(events.NewMessage(chats=channel))
        async def new_message_handler(event):
            await self.handle_new_message(event)
        
        print(f"Started monitoring channel {CHANNEL_USERNAME} for VLESS configurations...")
        await self.client.run_until_disconnected()

    async def cleanup(self):
        if self.session:
            await self.session.close()
        await self.client.disconnect()

async def main():
    scraper = TelegramChannelScraper(API_ID, API_HASH)
    try:
        await scraper.connect()
        await scraper.start_monitoring()
    finally:
        await scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 