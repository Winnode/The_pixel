import asyncio
import random
from fake_useragent import UserAgent
import aiohttp
import hashlib
import time
import base64
import json
from core.utils import logger
import re
from datetime import datetime


class ThePixel:
    def __init__(self, account_url: str, thread: int, proxy=None):
        self.account_url = account_url
        self.proxy = f"http://{proxy}" if proxy is not None else None
        self.thread = thread

        headers = {'User-Agent': UserAgent(platforms='mobile').random}

        # self.session = aiohttp.ClientSession(headers=headers, trust_env=True, cookies=aiohttp.CookieJar())
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True)

    async def login(self):
        resp = await self.session.put(self.account_url)

        resp_json = await resp.json()
        if resp_json and resp.status == 200:
            self.session.headers['Authorization'] = "Bearer " + resp_json.get('accessToken')
            return True

    async def get_player(self):
        resp = await self.session.get("https://thepixels.fireheadz.games/api/player", proxy=self.proxy)

        resp_json = await resp.json()
        if resp_json and resp.status == 200:
            return resp_json

    async def buy_booster(self):
        resp = await self.session.put("https://thepixels.fireheadz.games/api/shop/buy-booster/0", proxy=self.proxy)
        await asyncio.sleep(3)
        return resp.status == 200

    async def get_available_task(self, squad_id: str):
        if squad_id != "6240bb6f-78b0-4265-879d-ef55b54aa8d1":
            squad_id = await self.change_squad()

        resp = await self.session.get(f"https://thepixels.fireheadz.games/api/squads/{squad_id}", proxy=self.proxy)
        targets = (await resp.json()).get("targets")

        target_id = None
        for target in targets:
            if target["finishedAt"] is None and target['enabled'] and target['progress'] < 100:
                target_id = target['id']
                available_pixels = self.get_available_pixels(width=target['width'], x=target['x'], y=target['y'])
                break

        return target_id, available_pixels

    async def pixels(self, pixels: list, target_id: str):
        json_data = {
            "targetId": target_id,
            "pixels": pixels
        }
        resp = await self.session.put("https://thepixels.fireheadz.games/api/canvas/pixels", json=json_data, proxy=self.proxy)

        resp_json = await resp.json()
        if resp_json and resp.status == 200:
            next_draw_at = resp_json.get("nextDrawAt")

            unix_time = int(datetime.strptime(next_draw_at, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
            time_to_sleep = unix_time - datetime.utcnow().timestamp() + 1

            reward = resp_json.get("rewardCoins")

            return time_to_sleep+1, reward
        return False, resp_json

    async def change_squad(self):
        resp = await self.session.put("https://thepixels.fireheadz.games/api/squad/6240bb6f-78b0-4265-879d-ef55b54aa8d1/join")

        resp_json = await resp.json()
        if resp_json and resp.status == 200:
            await asyncio.sleep(2)
            return resp_json.get("squadId")

    @staticmethod
    def get_available_pixels(width: int, y: int, x: int, barrier=1024):
        available_point = []
        start_point = (barrier - y) * barrier + x

        while len(available_point) < width ** 2:
            for current_point in range(1, width + 1):
                available_point.append(start_point + current_point)
            start_point = barrier - width + start_point + current_point

        return available_point

    async def logout(self):
        await self.session.close()
