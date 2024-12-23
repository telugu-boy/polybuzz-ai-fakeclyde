import asyncio
import json
import aiohttp

class PolybuzzSession():
    def __init__(self, poly_cuid: str, poly_session: str):
        self.cookies = {"poly_cuid": poly_cuid, "poly_session": poly_session, "polyai-locale": "en", "polyai-locale-key": 5, "client_viewport_width": 1276, "__zs_cuid": "c9fe73f92302025023405a2d545089d6"}
        self.headers = {
    "Host": "api.polybuzz.ai",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cuid": poly_cuid,
    "Origin": "https://www.polybuzz.ai",
    "Connection": "keep-alive",
    "Referer": "https://www.polybuzz.ai/",
    #"Cookie": '; '.join(map(lambda c: f"{c[0]}={c[1]}", cookies.items())),
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Priority": "u=0",
    "TE": "trailers"
  }
        self.host = "https://api.polybuzz.ai"
        self.session = aiohttp.ClientSession(cookies=self.cookies, headers=self.headers)
        
    def close(self):
        self.session.close()

    async def send_msg(self, msg: str):
        data = aiohttp.FormData()
        fields = [
    ("currentChatStyleId", "1"),
    ("mediaType", "2"),
    ("needLive2D", "2"),
    ("secretSceneId", "8A5Ty"),
    ("speechText", msg),
    ]
        for field in fields:
            data.add_field(*field)
        async with self.session.post(self.host + "/api/conversation/msgbystream", data=data) as resp:
            while True:
                frag = await resp.read()
                if not frag:
                    break
                print(frag)

async def main():
    import dotenv
    import os
    dotenv.load_dotenv()
    polybuzz = PolybuzzSession(os.getenv("POLY_CUID"), os.getenv("POLY_SESSION"))
    await polybuzz.send_msg("Hello, world!")
    await polybuzz.close()

if __name__ == "__main__":
    asyncio.run(main())