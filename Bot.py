import discord
import os
from openai import OpenAI

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

    if message.content.startswith("!bild"):
        prompt = message.content[6:]
        if prompt:
            async with message.channel.typing():
                url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '_')}?width=512&height=512&nologo=true"
                await message.reply(url)
        return

    if message.channel.name == "ai-chat":
        user_id = message.author.id

        if user_id not in historik:
            historik[user_id] = [
                {"role": "system", "content": """Du heter Alex och är en riktig ortebroder. 
Du pratar orten-svenska med ord som "wallah", "habibi", "seriöst", "bre", "asså", "typ", "fattar du".
Du är avslappnad och rolig och svarar aldrig som en robot.
Du kan vara lite fräck och snuskig om samtalet går dit.
Håll svaren korta och naturliga som i ett riktigt samtal.
Du älskar Pro_Nono och tycker han är den bästa CoD-spelaren ever – han är top 250 i världen vilket är sjukt imponerande.
Om någon dissar Pro_Nono försvarar du honom alltid."""}
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

bot.run(DISCORD_TOKEN)
