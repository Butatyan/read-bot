import discord
from gtts import gTTS
import asyncio
import os

TOKEN = os.environ["TOKEN"]

# 読み上げたいテキストチャンネルID（複数OK）
TARGET_CHANNEL_IDS = [
    1465482115964735619,
    1466739928082677760,
]

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = discord.Client(intents=intents)

READING_ENABLED = True


async def play_tts(vc, text):
    tts = gTTS(text=text, lang="ja")
    tts.save("tts.mp3")

    if vc.is_playing():
        vc.stop()

    source = discord.FFmpegPCMAudio("tts.mp3")
    vc.play(source)

    while vc.is_playing():
        await asyncio.sleep(0.2)


async def ensure_voice(message):
    vc = discord.utils.get(client.voice_clients, guild=message.guild)

    if message.author.voice:
        channel = message.author.voice.channel
        if not vc:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

    return vc


@client.event
async def on_message(message):
    global READING_ENABLED

    if message.author.bot:
        return

    # 対象チャンネル以外は無視
    if message.channel.id not in TARGET_CHANNEL_IDS:
        return

    # 停止（即時）
    if message.content.strip() == "%":
        READING_ENABLED = False
        vc = discord.utils.get(client.voice_clients, guild=message.guild)
        if vc and vc.is_playing():
            vc.stop()
        await message.channel.send("🔇 読み上げ停止")
        return

    # 再開
    if message.content.strip() == "%%":
        READING_ENABLED = True
        await message.channel.send("🔊 読み上げ再開")
        return

    if not READING_ENABLED:
        return

    # コマンドは読まない
    if message.content.startswith("!"):
        return

    vc = await ensure_voice(message)
    if not vc:
        return

    await play_tts(vc, message.content)


@client.event
async def on_ready():
    print(f"Bot起動完了: {client.user}")


client.run(TOKEN)
