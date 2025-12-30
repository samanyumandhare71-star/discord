import os
import requests
import xml.etree.ElementTree as ET
from discord.ext import commands, tasks
from flask import Flask
from dotenv import load_dotenv

# -------------------- KEEP-ALIVE SERVER --------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host='0.0.0.0', port=3000)

# -------------------- DISCORD BOT --------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")  # Loaded from .env

CHANNEL_ID = 1149957260521512970
YT_CHANNEL = "UCFcUH5jvyTQomYz-sfKjs2Q"

bot = commands.Bot(command_prefix="!", intents=commands.Intents.all())
last_video = None

def get_latest_video_id():
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YT_CHANNEL}"
        xml_data = requests.get(url).text
        root = ET.fromstring(xml_data)

        # YouTube <yt:videoId>
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
                f"Click here to watch it 👇\n"
                f"https://www.youtube.com/watch?v={vid}"
            )
            print("Posted new upload alert!")
        else:
            print("Error: channel not found")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_upload.start()

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_server).start()
    bot.run(TOKEN)
