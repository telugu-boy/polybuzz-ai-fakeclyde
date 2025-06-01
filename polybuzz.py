import asyncio
import json

import aiohttp


class PolybuzzSession:
    def __init__(self, poly_cuid: str, poly_session: str):
        self.cookies = {
            "poly_cuid": poly_cuid,
            "polyai-locale": "en",
            "polyai-locale-key": 5,
            "session": poly_session,
            "client_viewport_width": 1276,
        }
        print()
        self.headers = {
            "Host": "api.polybuzz.ai",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.polybuzz.ai",
            "Connection": "keep-alive",
            "Referer": "https://www.polybuzz.ai/",
            "Cookie": "; ".join(map(lambda c: f"{c[0]}={c[1]}", self.cookies.items())),
            "Cuid": poly_cuid,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=0",
            "TE": "trailers",
        }
        self.host = "https://api.polybuzz.ai"
        self.session = aiohttp.ClientSession(cookies=self.cookies, headers=self.headers)

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def send_msg(self, msg: str, char: str) -> str:
        data = aiohttp.FormData()
        fields = [
            ("currentChatStyleId", "1"),
            ("mediaType", "2"),
            ("needLive2D", "2"),
            ("secretSceneId", char),
            ("speechText", msg),
        ]
        for field in fields:
            data.add_field(*field)
        async with self.session.post(
            self.host + "/api/conversation/msgbystream", data=data
        ) as resp:
            resp_msgs_raw = (await resp.read()).decode("UTF-8").split("\n")
            resp_msg = ""
            for rawmsg in resp_msgs_raw:
                try:
                    msg = json.loads(rawmsg)
                    resp_msg += msg["content"]
                except json.JSONDecodeError:
                    pass
        return resp_msg


class PolybuzzChar:
    def __init__(self, char: str, session: PolybuzzSession):
        self.char = char
        self.session = session

    async def send_msg(self, msg: str) -> str:
        return await self.session.send_msg(msg, self.char)


async def main():
    import os

    import dotenv

    dotenv.load_dotenv()
    async with PolybuzzSession(
        os.getenv("POLY_CUID"), os.getenv("POLY_SESSION")
    ) as polybuzz:
        emily = PolybuzzChar("8A5Ty", polybuzz)
        await emily.send_msg("Nooo pls im inocent")


if __name__ == "__main__":
    asyncio.run(main())
