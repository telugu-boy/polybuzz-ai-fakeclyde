import asyncio
import aiohttp

class PolybuzzSession():
    def __init__(self, poly_uid: str, poly_session: str):
        self.cookies = {"poly_cuid": poly_uid, "poly_session": poly_session, "polyai-locale": "en", "polyai-locale-key": 5, "client_viewport_width": 1276}
        self.headers = {
    "Host": "api.polybuzz.ai",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cuid": "tourist_8a9dac4e-3acc-4df6-8ee8-32173e9e3668-774973",
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
        self.session = aiohttp.ClientSession(cookies=self.cookies, headers=self.headers)
    
    def close(self):
        self.session.close()

def main():
    pass

if __name__ == "__main__":
    asyncio.run(main())