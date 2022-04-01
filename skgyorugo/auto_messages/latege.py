from aptbot.bot import Message, Commands, Bot
import datetime as dt
from datetime import datetime
import tools.smart_start_stream_time

COOLDOWN = 120
END_TIME = COOLDOWN * 6

STREAM_SCHEDULE = dt.time(17, 30)


def main(bot: Bot, message: Message):
    start_stream_ts = tools.smart_start_stream_time.start_stream_timestamp()
    if not start_stream_ts:
        return
    start_stream_dt = datetime.utcfromtimestamp(start_stream_ts)
    stream_schedule_dt = datetime.combine(datetime.now(), STREAM_SCHEDULE)
    latege_amount = (start_stream_dt - stream_schedule_dt).total_seconds()
    if latege_amount > 45 * 60:
        msg = f"{message.channel} is so Latege he might as well have not \
            streamed today. At least he's early for tomorrow COPIUM . \
            {message.channel} is Latege by {latege_amount} seconds Madge"
    elif latege_amount > 0:
        msg = f"{message.channel} is Latege by {latege_amount} seconds again Madge"
    elif latege_amount == 0:
        msg = f"Amazing!!! {message.channel} is EXACTLY on time today ihaspeHappy"
    else:
        msg = f"UNBELIEVABLE!!!!! {message.channel} is EARLY by {-latege_amount} seconds!!!!\
        This has NEVER happened before POGGERS"
    bot.send_privmsg(message.channel, msg)
