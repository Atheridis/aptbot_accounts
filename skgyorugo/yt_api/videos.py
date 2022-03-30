from yt_api import *


@dataclass
class Video:
    video_name: str
    video_id: str


def get_newest_video(channel_id: str) -> Optional[Video]:
    get_video_snippets = "?part=snippet"
    get_url = URL + get_video_snippets + \
        f"&channelId={channel_id}&order=date&type=video" + f"&key={API}"

    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        get_url,
    )
    print(f"the r.status is {r.status}")
    if r.status != 200:
        return None
    data = json.loads(r.data.decode("utf-8"))["items"][0]
    video_id = data["id"]["videoId"]
    video_title = data["snippet"]["title"]

    return Video(video_title, video_id)
