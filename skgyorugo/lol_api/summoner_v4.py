from lol_api import *

logger = logging.getLogger(__name__)


@dataclass
class Summoner:
    summoner_id: str
    account_id: str
    puuid: str
    name: str
    profile_icon_id: int
    revision_date: int
    summoner_level: int


def get_summoner_from_puuid(puuid: str) -> Optional[Summoner]:
    endpoint = f"/lol/summoner/v4/summoners/by-puuid/{puuid}"
    url = BASE_URL + endpoint
    logger.debug(f"url is: {url}")
    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        url,
        headers=HEADER,
    )
    if r.status != 200:
        logger.warning(
            f"Couldn't retrieve summoner with puuid: {puuid}. Status code {r.status}"
        )
        return None
    data = json.loads(r.data.decode("utf-8"))
    return Summoner(
        data["id"],
        data["accountId"],
        data["puuid"],
        data["name"],
        data["profileIconId"],
        data["revisionDate"],
        data["summonerLevel"],
    )


def get_summoner_from_name(name: str) -> Optional[Summoner]:
    endpoint = f"/lol/summoner/v4/summoners/by-name/{name}"
    url = BASE_URL + endpoint
    logger.debug(f"url is: {url}")
    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        url,
        headers=HEADER,
    )
    if r.status != 200:
        logger.warning(f"Couldn't retrieve summoner: {name}. Status code {r.status}")
        return None
    data = json.loads(r.data.decode("utf-8"))
    return Summoner(
        data["id"],
        data["accountId"],
        data["puuid"],
        data["name"],
        data["profileIconId"],
        data["revisionDate"],
        data["summonerLevel"],
    )
