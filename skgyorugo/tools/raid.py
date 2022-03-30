import ttv_api.channel
from aptbot.bot import Bot, Message, Commands


def raid(bot: Bot, message: Message):
    if message.command == Commands.USERNOTICE and message.tags["msg-id"] == "raid":
        raider_name = message.tags["msg-param-displayName"]
        raider_login = message.tags["msg-param-login"]
        raider_id = message.tags["user-id"]
        raider_channel_info = ttv_api.channel.get_channels(raider_id)
        raider_game = ""
        if raider_channel_info:
            raider_game = raider_channel_info[0].game_name
        viewers = message.tags["msg-param-viewerCount"]
        viewers = f"{viewers} viewer" if viewers == "1" else f"{viewers} viewers"
        msg_reply = f"POGGERS {raider_name} has raided {message.channel} \
                    with {viewers}!!! Why don't you check them out at: \
                    https://twitch.tv/{raider_login}"
        if raider_game:
            msg_reply += f" they were just playing {raider_game}!"
        bot.send_privmsg(message.channel, msg_reply)
