import asyncio
import datetime
from typing import Any, Dict, List, Optional
import discord
from characterai import PyAsyncCAI
import sys
import os
from dateutil import parser
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

cmd_prefix = "GURSSY, pwease "
owner_ids = [787576039093043202, 1088556537712226306]
approved_channels = [1088566537415303320, 1080667873900507197, 1146702758204932106, 1185316995625914409, 1230119579574079538]


class FakeClyde(discord.Client):
    def __init__(self, **options: Any) -> None:
        self.caiclient = PyAsyncCAI(os.environ.get("CHARACTERAI_TOKEN"), plus=True)
        self.author_dict: Optional[Dict[str, str]] = None
        self.character_id: Optional[str] = "WT_DrON26OESd8JtstJ5F0e0YM_RgEctUicLYZ-KhS8"
        self.chats: Optional[List] = None
        self.curr_chat: Optional[dict] = None
        super().__init__(**options)

    @property
    def character_name(self) -> Optional[str]:
        try:
            return next(
                filter(
                    lambda x: x["author"]["name"] != self.author_dict["name"],
                    self.curr_chat["preview_turns"],
                )
            )["author"]["name"]
            # return self.curr_chat["preview_turns"][0]["author"]["name"]
        except Exception as e:
            print(e)
            return None

    async def on_ready(self):
        self.author_dict = await self.get_author_dict()
        self.chats = await self.fetch_character_chats()
        self.curr_chat = self.chats[0]
        print(
            f"Ready - Connected to {self.user.name} and character.ai as {self.author_dict['name']}"
        )

    async def get_author_dict(self):
        user = await self.caiclient.user.info()
        user = user["user"]
        username = user["user"]["username"]
        author_id = str(user["user"]["id"])
        return {"author_id": author_id, "is_human": True, "name": username}

    async def fetch_character_chats(self):
        async with self.caiclient.connect() as chat2:
            try:
                chats: List[Dict[str, str]] = (
                    await chat2.get_histories(self.character_id)
                )["chats"]
            except KeyError:
                chats = []
            for chat in chats:
                chat["create_time"] = parser.parse(chat["create_time"])
            chats.sort(key=lambda x: x["create_time"], reverse=True)
        self.chats = chats
        return self.chats


bot = FakeClyde(chunk_guilds_at_startup=False)


async def show_chats():
    chats_msgs = []
    for idx, chat in enumerate(bot.chats):
        chats_msg = (
            f"Chat {idx+1}, created at <t:{int(chat['create_time'].timestamp())}:f>"
        )
        if chat["chat_id"] == bot.curr_chat["chat_id"]:
            chats_msg += " (current)"
        chats_msgs.append(chats_msg)
    return f"{bot.character_name}:\n\n" + "\n".join(chats_msgs)


async def create_new_chat():
    async with bot.caiclient.connect() as chat2:
        new_chat = (
            await chat2.new_chat(
                bot.character_id,
                str(datetime.datetime.now()),
                bot.author_dict["author_id"],
            )
        )[0]
    bot.chats.insert(0, new_chat["chat"])
    return new_chat


@bot.event
async def on_message(message: discord.Message):
    if message.channel.id not in approved_channels:
        return

    if message.author.id in owner_ids:
        if message.content.startswith(cmd_prefix + "switch character to"):
            old_char_id = bot.character_id
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

    if message.reference:
        referred_message = await message.channel.fetch_message(
            message.reference.message_id
        )
    else:
        referred_message = message
    if message.author.id != bot.user.id and (
        f"<@{bot.user.id}>" in message.content
        or referred_message.author.id == bot.user.id
    ):
        print(f"got message from {message.author.name}")
        # scrub out mentions
        prompt = message.content.replace(f"<@{bot.user.id}>", "")
        async with message.channel.typing():
            async with bot.caiclient.connect() as chat2:
                send_message_args = (
                    bot.character_id,
                    bot.curr_chat["chat_id"],
                    f"{message.author.display_name} says: " + prompt,
                    bot.author_dict,
                )
                response = await chat2.send_message(*send_message_args)
                while "raw_content" not in response["turn"]["candidates"][0]:
                    response = await chat2.send_message(*send_message_args)
        print(response["turn"]["candidates"][0])
        await message.reply(response["turn"]["candidates"][0]["raw_content"])


def main():
    if len(sys.argv) > 1:
        bot.character_id = sys.argv[1]
    print(f"using character id {bot.character_id}")
    bot.run(os.environ.get("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()

