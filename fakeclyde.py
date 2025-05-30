import asyncio
import datetime
from typing import Any, Dict, List, Optional
import discord
from polybuzz import PolybuzzSession, PolybuzzChar
import sys
import os
from dateutil import parser
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

cmd_prefix = "GURSSY, pwease "
owner_ids = [787576039093043202]
approved_channels = [
    1088566537415303320,1325761177287921696,
    1312605220026712145,
]

class PolybuzzFakeClyde(discord.Client):
    def __init__(self, **options: Any) -> None:
        self.polybuzz: PolybuzzSession
        self.char: PolybuzzChar
        self.character_id = "pCBb4"
        super().__init__(**options)

    async def on_ready(self):
        # set polybuzz stuff on ready with async event loop:
        self.polybuzz = PolybuzzSession(os.getenv("POLY_CUID"), os.getenv("POLY_SESSION"))
        self.char = PolybuzzChar(self.character_id, self.polybuzz)
        print(
            f"Ready - Connected to {self.user.name} and polybuzz.ai"
        )
    
    async def on_message(self, message: discord.Message):
        if message.channel.id not in approved_channels:
            return

        """
        if message.author.id in owner_ids:
            if message.content.startswith(cmd_prefix + "switch character to"):
                old_char_id = self.character_id
                bot.character_id = message.content.split(" ")[-1]
                await bot.fetch_character_chats()
                if len(bot.chats) == 0:
                    try:
                        new_chat = await create_new_chat()
                    except Exception as e:
                        bot.character_id = old_char_id
                        await message.add_reaction("❌")
                        return
                bot.curr_chat = bot.chats[0]
                chats_msg_reply = await show_chats()
                await message.reply(chats_msg_reply)
                return

            if message.content == cmd_prefix + "show chats":
                await bot.fetch_character_chats()
                chats_msg_reply = await show_chats()
                await message.reply(chats_msg_reply)
                return

            if message.content.startswith(cmd_prefix + "switch chat to "):
                chat_idx = int(message.content.split(" ")[-1]) - 1
                if chat_idx >= len(bot.chats):
                    await message.add_reaction("❌")
                    return
                bot.curr_chat = bot.chats[chat_idx]
                await message.add_reaction("✅")
                return

            if message.content == cmd_prefix + "create new chat":
                new_chat = await create_new_chat()
                bot.curr_chat = new_chat["chat"]
                await message.add_reaction("✅")
                return
        """

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
