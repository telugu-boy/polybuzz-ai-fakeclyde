import asyncio
import os
import re
import sys
from yt_dlp import YoutubeDL

import discord
from dotenv import find_dotenv, load_dotenv

from polybuzz import PolybuzzChar, PolybuzzSession

load_dotenv(find_dotenv())

cmd_prefix = "GURSSY, pwease "
owner_ids = [787576039093043202]
approved_channels = [
    1088566537415303320,
    1325761177287921696,
    1312605220026712145,
]


class PolybuzzFakeClyde(discord.Client):
    def __init__(self, **options) -> None:
        self.polybuzz: PolybuzzSession
        self.char: PolybuzzChar
        self.character_id = "pCBb4"
        super().__init__(**options)

    async def on_ready(self):
        # set polybuzz stuff on ready with async event loop:
        self.polybuzz = PolybuzzSession(
            os.getenv("POLY_CUID"), os.getenv("POLY_SESSION")
        )
        self.char = PolybuzzChar(self.character_id, self.polybuzz)
        print(f"Ready - Connected to {self.user.name} and polybuzz.ai")


    def fbmatch(self, content: str):
        fbpattern = r"https:\/\/www\.facebook\.com\/share\/[^\/]+\/[A-Za-z0-9]+\/?"
        match = re.search(fbpattern, content)

        if not match:
            return

        url = match.group()

        ydl_opts = {
            'format': 'hd',
            'quiet': True,
            'skip_download': True,
            'forceurl': True,
            'noplaylist': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                # Get the direct video URL for the selected format
                return info.get('url')
            except Exception as e:
                print(f"Error extracting video URL: {e}")
                return


    async def on_message(self, message: discord.Message):
        if message.channel.id not in approved_channels:
            return

        # match regex for fb share links
        fburl = self.fbmatch(message.content)
        if fburl:
            print(f"got fb message from {message.author.name}")
            await message.channel.send(f"[vid link]({fburl})")

        if message.reference:
            referred_message = await message.channel.fetch_message(
                message.reference.message_id
            )
        else:
            referred_message = message

        if message.author.id != self.user.id and (
            f"<@{self.user.id}>" in message.content
            or referred_message.author.id == self.user.id
        ):
            print(f"got message from {message.author.name}")
            # scrub out mentions
            prompt = message.content.replace(f"<@{self.user.id}>", "")
            prompt = message.author.name + ": " + prompt
            async with message.channel.typing():
                response = await self.char.send_msg(prompt)
                print(response)
            await message.reply(response)


bot = PolybuzzFakeClyde(chunk_guilds_at_startup=False)


async def main():
    if len(sys.argv) > 1:
        bot.character_id = sys.argv[1]
    print(f"using character id {bot.character_id}")
    await bot.start(os.environ.get("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
