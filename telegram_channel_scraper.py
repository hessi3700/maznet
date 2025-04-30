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

# Configuration
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', 'Maznet')
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
        self.configs = []  # We'll only keep the latest config
        self.session = None
        self.kv_url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/latest_configs"
        self.headers = {
            "Authorization": f"Bearer {CF_API_TOKEN}",
            "Content-Type": "application/json"
        }

    async def initialize_kv(self):
        """Initialize KV storage with the latest config from channel"""
        try:
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
                        config_data = {
                            'config': vless_configs[0],  # Take the first config from the message
                            'date': message.date.isoformat(),
                            'message_id': message.id
                        }
                        all_configs.append(config_data)
                        break  # We only need the latest config
            
            # Sort configs by date (newest first)
            all_configs.sort(key=lambda x: x['date'], reverse=True)
            
            # Only keep the latest config
            self.configs = all_configs[:1] if all_configs else []
            
            # Save to KV
            if self.configs:
                await self.update_kv()
                print(f"Successfully initialized KV with latest config")
                print(f"Latest config: {self.configs[0]['config']}")
            else:
                print("No VLESS configs found in the channel")
                
        except Exception as e:
            print(f"Error initializing KV: {e}")
            import traceback
            print(traceback.format_exc())

    async def connect(self):
        await self.client.start()
        self.session = aiohttp.ClientSession()
        print("Connected to Telegram!")
        await self.initialize_kv()

    def extract_vless_config(self, text):
        """Extract VLESS configurations from text"""
        vless_pattern = r'vless://[^\s`]+'
        matches = re.findall(vless_pattern, text)
        return matches

    async def update_kv(self):
        """Update KV storage with current configs"""
        if not self.session or not self.configs:
            return

        try:
            data = {"value": json.dumps(self.configs)}
            async with self.session.put(self.kv_url, headers=self.headers, json=data) as response:
                if response.status == 200:
                    print("Successfully updated KV storage")
                else:
                    print(f"Failed to update KV: {response.status}")
                    print(await response.text())
        except Exception as e:
            print(f"Error updating KV: {e}")

    async def handle_new_message(self, event):
        try:
            message = event.message
            if not message.text:
                return

            # Extract VLESS configs from the message
            vless_configs = self.extract_vless_config(message.text)
            
            if vless_configs:
                # Only keep the latest config
                self.configs = [{
                    'config': vless_configs[0],
                    'date': message.date.isoformat(),
                    'message_id': message.id
                }]
                print(f"New VLESS config found: {vless_configs[0]}")
                await self.update_kv()
            
            # Save the full message
            message_data = {
                'id': message.id,
                'date': message.date.isoformat(),
                'text': message.text,
                'views': message.views if hasattr(message, 'views') else None,
                'forwards': message.forwards if hasattr(message, 'forwards') else None
            }
            self.messages.append(message_data)
            
        except Exception as e:
            print(f"Error handling message: {e}")
            import traceback
            print(traceback.format_exc())

    async def start_monitoring(self):
        channel = await self.client.get_entity(CHANNEL_USERNAME)
        
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