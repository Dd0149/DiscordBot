import discord
import asyncio
import random
import datetime
import os

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

TOKEN = 'YOUR_TOKEN_HERE'
FOLDER_PATH = 'PLACEFOLDER'
TARGET_KEYWORDS = ['weta', 'unity', 'vfx', 'ai', 'ubuntu', 'software development', 'python']

# Global variable to track image index
image_index = 0

async def post_next_image():
    global image_index
    
    # Get a list of image files from the specified folder
    image_files = [file for file in os.listdir(FOLDER_PATH) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        print("No image files found in the folder.")
        return
    
    if image_index >= len(image_files):
        print("All images have been posted.")
        return
    
    selected_image = image_files[image_index]
    image_path = os.path.join(FOLDER_PATH, selected_image)

    # Get the text for the blog from the file
    text_for_blog = await get_text_for_blog()

    # Replace 'YOUR_GUILD_ID' and 'YOUR_CHANNEL_ID' with the actual IDs
    guild_id = YOUR_GUILD_ID
    channel_id = YOUR_CHANNEL_ID

    # Fetch the guild and channel
    guild = client.get_guild(guild_id)
    if not guild:
        print("Guild not found.")
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        print("Channel not found.")
        return

    # Create a message with the image and text
    message = f"Hi everyone! Here's the image of the day:\n{image_path}\n\n{text_for_blog}"
    
    try:
        with open(image_path, 'rb') as image_file:
            await channel.send(content=message, file=discord.File(image_file))
            print("Image posted!")
            image_index += 1
    except Exception as e:
        print(f"Error posting image: {e}")

async def daily_announcement(daily_message):
    print(daily_message)

async def list_files_and_folders():
    for root, dirs, files in os.walk(FOLDER_PATH):
        print(f"Files in folder {root}:")
        for file in files:
            print(file)
        print(f"Subfolders in folder {root}:")
        for dir in dirs:
            print(dir)

async def get_text_for_blog():
    with open('discord_blog_line.txt', 'r') as file:
        return file.read()

async def search_relevant_channels():
    for guild in client.guilds:
        for channel in guild.text_channels:
            async for message in channel.history(limit=100):
                content = message.content.lower()
                if any(keyword in content for keyword in TARGET_KEYWORDS):
                    print(f"Found relevant message in {channel.name} - {message.content}")

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

        await list_files_and_folders()
        text_for_blog = await get_text_for_blog()
        await post_next_image()
        await search_relevant_channels()

        daily_message = await get_text_for_blog()  # Use the same text for the daily message
        await daily_announcement(daily_message)

        await asyncio.sleep(24 * 60 * 60)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

    client.loop.create_task(scheduled_task())

client.run(TOKEN)

