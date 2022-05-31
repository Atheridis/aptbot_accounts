from aptbot.bot import Message, Commands, Bot
import yt_api.videos

COOLDOWN = 25 * 60
END_TIME = 0

CHANNEL_ID = "UCQ7C3NUKY6TSkURdUdVoYFw"


def main(bot: Bot, message: Message):
    video = yt_api.videos.get_newest_video(CHANNEL_ID)
    if video:
        video_link = f"https://www.youtube.com/watch?v={video.video_id}"
        msg = f'Watch Peks\' latest video "{video.video_name}" here: {video_link}'
    else:
        msg = f"Check out my youtube channel here -> https://www.youtube.com/channel/{CHANNEL_ID}"
    bot.send_privmsg(message.channel, msg)
