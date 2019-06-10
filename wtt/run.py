import asyncio
import logging
from queue import Queue
from threading import Thread

import wtt.telegram_client.telegram_bot as tgBot
import wtt.telegram_client.telegram_selfbot as tgSelfBot
import wtt.utils as utils
import wtt.whatsapp_client.wtt_stack as wttStack
from wtt.dao import WTTDao
from wtt.telegram_client.tg_bus import TGBus
from wtt.whatsapp_client.wa_bus import WABus

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def loopInThread(aloop, tgsQueue, config, dao):
    aloop.run_until_complete(tgSelfBot.run(tgsQueue, config, dao))


if __name__ == "__main__":
    if utils.loadConfig():
        loop = asyncio.get_event_loop()

        dao = WTTDao("chatmap.db")
        wttQ = Queue(maxsize=0)
        ttwQ = Queue(maxsize=0)
        tgsQ = Queue(maxsize=0)

        waBus = WABus(wttQ, ttwQ)
        tgBus = TGBus(wttQ, ttwQ, tgsQ)

        loop.run_until_complete(utils.ensureTelethonSession())

        tgs_thread = Thread(target=loopInThread, args=(loop, tgsQ, utils.getTgConfig(), dao))
        tg_thread = Thread(target=tgBot.run, args=(tgBus, utils.getTgConfig(), dao))
        wa_thread = Thread(target=wttStack.run, args=(waBus, utils.getWaConfig(), dao))

        try:
            tgs_thread.start()
            tg_thread.start()
            wa_thread.start()
        except KeyboardInterrupt:
            tgs_thread.join()
            tg_thread.join()
            wa_thread.join()
            wttQ.join()
            ttwQ.join()
            tgsQ.join()
