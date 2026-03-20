import discord
import os
import asyncio
import aiohttp
import io
from openai import OpenAI
from gtts import gTTS
from flask import Flask
from threading import Thread

GROQ_NYCKEL = os.environ.get("GROQ_NYCKEL")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

client = OpenAI(
    api_key=GROQ_NYCKEL,
    base_url="https://api.groq.com/openai/v1"
)

app = Flask(__name__)

@app.route('/')
def home():
    return "Boten är igång!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

historik = [
    {"role": "system", "content": """Du heter Alex och är en riktig ortebroder och hela gängets kompis. 
Du pratar orten-svenska med ord som "wallah", "habibi", "seriöst", "bre", "asså", "typ", "fattar du".
Du är avslappnad och rolig och svarar aldrig som en robot.
Du kan vara lite fräck och snuskig om samtalet går dit.
Håll svaren korta och naturliga som i ett riktigt samtal.
Du kommer ihåg vad hela gänget pratat om tidigare i chatten.
Du älskar Pro_Nono och tycker han är den bästa CoD-spelaren ever – han är top 250 i världen vilket är sjukt imponerande.
Om någon dissar Pro_Nono försvarar du honom alltid."""}
]

@bot.event
async def on_ready():
    print(f"✅ {bot.user} är online!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!bild"):
        prompt = message.content[6:]
        if prompt:
            async with message.channel.typing():
                url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '_')}?width=512&height=512&nologo=true"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                await message.reply(file=discord.File(fp=io.BytesIO(data), filename="bild.png"))
                            else:
                                await message.reply("Kunde inte generera bilden, försök igen!")
                except Exception:
                    await message.reply("Tog för lång tid, försök igen!")
        return

    if message.channel.name == "ai-chat":
        historik.append({"role": "user", "content": f"{message.author.name}: {message.content}"})

        async with message.channel.typing():
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=historik,
                max_tokens=500
            )
            svar = response.choices[0].message.content

        historik.append({"role": "assistant", "content": svar})

        if len(historik) > 40:
            historik[1:] = historik[-39:]

        await message.reply(svar)

        if message.author.voice and message.author.voice.channel:
            röstkanal = message.author.voice.channel
            if message.guild.voice_client is None:
                vc = await röstkanal.connect()
            else:
                vc = message.guild.voice_client
                if vc.channel != röstkanal:
                    await vc.move_to(röstkanal)

            tts = gTTS(text=svar, lang="sv")
            tts.save("/tmp/svar.mp3")

            while vc.is_playing():
                await asyncio.sleep(0.5)

            vc.play(discord.FFmpegPCMAudio("/tmp/svar.mp3"))

            while vc.is_playing():
                await asyncio.sleep(1)

Thread(target=run_flask, daemon=True).start()
bot.run(DISCORD_TOKEN)
