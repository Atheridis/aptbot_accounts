from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg
import urllib3
import os

PERMISSION = 99
PREFIX = '?'
DESCRIPTION = ""
USER_COOLDOWN = 90
GLOBAL_COOLDOWN = 60

OAUTH = os.getenv("APTBOT_OAUTH")
CLIENT_ID = os.getenv("APTBOT_CLIENT_ID")

HEADER = {
    "Authorization": f"Bearer {OAUTH}",
    "Client-Id": f"{CLIENT_ID}",
    "Content-Type": "application/json",
}


def main(bot: Bot, message: Message):
    http = urllib3.PoolManager()
    r1 = http.request(
        "GET",
        f"https://twitch.center/customapi/bttvemotes?channel={message.channel}",
        headers=HEADER,
    )
    r2 = http.request(
        "GET",
        f"https://twitch.center/customapi/ffzemotes?channel={message.channel}",
        headers=HEADER,
    )

    if r1.status != 200 or r2.status != 200:
        bot.send_privmsg(
            message.channel,
            "NotLikeThis oopsie woopsie, we've made a fucky wucky. We can't \
            get the emotes at the moment. Hopefuwwy UwU wiww wait patientwy \
            tiww we get thiws pwobwem sowted. OwO"
        )
        return
    emotes = r1.data.decode("utf-8")
    emotes += " " + r2.data.decode("utf-8")
    tools.smart_privmsg.send(bot, message, emotes)
