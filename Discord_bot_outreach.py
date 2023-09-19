import discord
import asyncio
import random
import datetime
import os
import sqlite3

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

TOKEN = 'YOUR_TOKEN_HERE'
FOLDER_PATH = 'PLACEFOLDER'
TARGET_KEYWORDS = ['weta', 'unity', 'vfx', 'ai', 'ubuntu', 'software development', 'python']

# SQLite setup
conn = sqlite3.connect('search_results.db')
cursor = conn.cursor()

# Create table if not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY,
    keyword TEXT,
    channel_name TEXT,
    guild_name TEXT,
    frequency INTEGER
)
''')
conn.commit()

# Monte Carlo Sampling of Keywords
def sample_keywords(target_keywords):
    num_keywords = random.randint(1, len(target_keywords))
    return random.sample(target_keywords, num_keywords)

async def search_relevant_channels():
    for guild in client.guilds:
        for channel in guild.text_channels:
            message_count = {}
            async for message in channel.history(limit=100):
                for keyword in sample_keywords(TARGET_KEYWORDS):  # Monte Carlo sampling
                    if keyword in message.content.lower():
                        if keyword not in message_count:
                            message_count[keyword] = 0
                        message_count[keyword] += 1

            for keyword, count in message_count.items():
                cursor.execute("INSERT INTO results (keyword, channel_name, guild_name, frequency) VALUES (?, ?, ?, ?)", 
                               (keyword, channel.name, guild.name, count))
    conn.commit()

async def scheduled_task():
    await client.wait_until_ready()

    while not client.is_closed():
        now = datetime.datetime.now()
        random_hour = random.randint(8, 10)
        random_minute = random.randint(0, 59)
        scheduled_time = datetime.time(hour=random_hour, minute=random_minute)
        target_time = datetime.datetime.combine(datetime.date.today(), scheduled_time)

        if now.time() >= scheduled_time:
            target_time += datetime.timedelta(days=1)

        time_to_wait = (target_time - now).total_seconds()

        await asyncio.sleep(time_to_wait)
        print(f"Executing scheduled task at {datetime.datetime.now()}")

        await search_relevant_channels()

        await asyncio.sleep(24 * 60 * 60)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    client.loop.create_task(scheduled_task())

client.run(TOKEN)
