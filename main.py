import os
import requests
import xml.etree.ElementTree as ET
from discord.ext import tasks, commands
from flask import Flask
from threading import Thread

# -------------------- KEEP BOT ONLINE --------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host='0.0.0.0', port=3000)

# -------------------- DISCORD BOT --------------------
# Read token from GitHub secret
TOKEN = os.getenv("DISCORD_TOKEN")

# Replace with your Discord channel ID
CHANNEL_ID = 1149957260521512970

# Replace with your YouTube channel ID
YT_CHANNEL = "UCFcUH5jvyTQomYz-sfKjs2Q"

bot = commands.Bot(command_prefix="!", intents=commands.Intents.all())
last_video = None

def get_latest_video_id():
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YT_CHANNEL}"
        xml_data = requests.get(url).text
        root = ET.fromstring(xml_data)
        for child in root.iter('{http://www.youtube.com/xml/schemas/2015}videoId'):
            return child.text
    except Exception as e:
        print("Error fetching video:", e)
        return None

@tasks.loop(seconds=20)
async def check_upload():
    global last_video
    vid = get_latest_video_id()

    if vid and vid != last_video:
        last_video = vid
        channel = bot.get_channel(CHANNEL_ID)

        if channel:
            await channel.send(
                f"@everyone\n"
                f"**Roti Gaming just uploaded a new video on YouTube!** 🔥\n"
                f"Click here to watch 👇\n"
                f"https://www.youtube.com/watch?v={vid}"
            )
            print("Posted new upload alert!")
        else:
            print("Error: channel not found")

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    check_upload.start()

if __name__ == "__main__":
    # Start Flask server to keep the bot online
    Thread(target=run_server).start()
    bot.run(TOKEN)
