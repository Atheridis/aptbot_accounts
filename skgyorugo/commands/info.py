from aptbot.bot import Message, Commands, Bot
import tools.smart_start_stream_time

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = ""
USER_COOLDOWN = 5
GLOBAL_COOLDOWN = 2


def main(bot: Bot, message: Message):
    start_stream_ts = tools.smart_start_stream_time.start_stream_timestamp()
    if not start_stream_ts:
        msg = r"The Sponsor is World of Warships, which is a historical strategy online combat PC game. It looks very 5Head but i will conquer elmoFire so imma be testing it out. If u want to join in with us, try it urself, or if you just want to help me out Gladge u can sign up with my link: https://strms.net/warships_ihaspeks you get a fair few bonuses for using mah link too ihaspeBased and after u have won your first game and bought ur first ship ill get a notification on stream peksJAM"
    else:
        msg = r"Peks is live so he can awnser that KEKW but here is the link just in case BASED https://strms.net/warships_ihaspeks"
    tools.smart_privmsg.send_safe(bot, message.channel, msg)

