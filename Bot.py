import discord
import os
import asyncio
from openai import OpenAI
from gtts import gTTS

GROQ_NYCKEL = os.environ.get("GROQ_NYCKEL")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

client = OpenAI(
    api_key=GROQ_NYCKEL,
    base_url="https://api.groq.com/openai/v1"
)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

historik = {}

@bot.event
async def on_ready():
    print(f"✅ {bot.user} är online!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == "ai-chat":
        user_id = message.author.id

        if user_id not in historik:
            historik[user_id] = [
                {"role": "system", "content": """Du heter Alex och är användarens bästa kompis. 
Du är en avslappnad svensk kille, pratar med slang och är rolig.
Du svarar aldrig som en robot - alltid som en riktig vän.
Du kan vara lite fräck och snuskig om samtalet går dit.
Håll svaren korta och naturliga som i ett riktigt samtal."""}
            ]

        historik[user_id].append({"role": "user", "content": message.content})

        async with message.channel.typing():
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=historik[user_id],
                max_tokens=500
            )
            svar = response.choices[0].message.content

        historik[user_id].append({"role": "assistant", "content": svar})

        if len(historik[user_id]) > 20:
            historik[user_id] = [historik[user_id][0]] + historik[user_id][-19:]

        await message.reply(svar)

        # Kolla om användaren är i en röstkanal
        if message.author.voice and message.author.voice.channel:
            röstkanal = message.author.voice.channel

            # Generera tal med gTTS
            tts = gTTS(text=svar, lang="sv")
            tts.save("svar.mp3")

            # Gå med i röstkanalen och spela upp
            if message.guild.voice_client is None:
                vc = await röstkanal.connect()
            else:
                vc = message.guild.voice_client
                await vc.move_to(röstkanal)

            vc.play(discord.FFmpegPCMAudio("svar.mp3"))

            # Vänta tills den är klar sen lämna
            while vc.is_playing():
                await asyncio.sleep(1)

            await vc.disconnect()

bot.run(DISCORD_TOKEN)
```
