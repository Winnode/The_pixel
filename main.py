import asyncio
from core.utils.logger import logger
import asyncio
import random
from core.thepixel import ThePixel
from core.utils import logger, get_all_lines


async def PB(thread, account):
    logger.info(f"Thread {thread} | Start work")
    if not account:
        return

    if '::' in account:
        private_key, proxy = account.split('::')
    else:
        proxy = None

    pixel = ThePixel(account_url=account, thread=thread, proxy=proxy)

    if await pixel.login():
        while True:
            player = await pixel.get_player()
            if player:
                balance = int(player['coins'])
                have_booster = True if player['activeBoosters'] else False
                target_id, available_pixels = await pixel.get_available_task(squad_id=player['squad']['id'])

                if balance >= 1000 and not have_booster:
                    if await pixel.buy_booster():
                        logger.success(f"Thread {thread} | Buy x2 booster!")

                        have_booster = True
                        balance -= 1000
                    else:
                        logger.error(f"Thread {thread} | Can't buy x2 booster!")

                pixels = [{"id": random.choice(available_pixels), "color": 4294967295}]
                if have_booster:
                    pixels.append({"id": pixels[0]['id']+1, "color": pixels[0]['color']})

                time_to_sleep, reward = await pixel.pixels(pixels=pixels, target_id=target_id)
                if time_to_sleep:
                    logger.success(f"Thread {thread} | Pushed {len(pixels)} pixel(s), reward: {reward}; balance: {balance+reward}")
                    await asyncio.sleep(time_to_sleep)
                else:
                    logger.error(f"Thread {thread} | Error pushed {len(pixels)} pixel(s): {reward}")
                    await asyncio.sleep(10)

    await pixel.logout()
    logger.info(f"Thread {thread} | Finished work")


async def main():
    print("Winnode")

    tasks = []
    for thread, account in enumerate(get_all_lines('data/accounts.txt')):
        tasks.append(asyncio.create_task(PB(thread, account)))

    print(f"tasks: {len(tasks)}")

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

