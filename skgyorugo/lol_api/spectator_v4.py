from lol_api import *
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(name)s; %(message)s")

file_handler = logging.FileHandler("/var/log/aptbot/logs.log")
file_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(file_handler)


@dataclass
class BannedChampion:
    pick_turn: int
    champion_id: int
    team_id: int


@dataclass
class Perks:
    perk_ids: list[int]
    perk_style: int
    perk_sub_style: int


@dataclass
class CurrentGameParticipant:
    champion_id: int
    perks: Perks
    profile_icon_id: int
    bot: bool
    team_id: int
    summoner_name: str
    summoner_id: str
    spell1_id: int
    spell2_id: int


@dataclass
class GameInfo:
    game_id: int
    game_type: str
    game_start_time: int
    map_id: int
    game_length: int
    platform_id: str
    game_mode: str
    banned_champions: list[BannedChampion]
    game_queue_config_id: Optional[int]
    observers: str
    participants: list[CurrentGameParticipant]


def get_spectator_info_from_summoner_id(summoner_id: str) -> Optional[GameInfo]:
    endpoint = f"/lol/spectator/v4/active-games/by-summoner/{summoner_id}"
    url = BASE_URL + endpoint
    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        url,
        headers=HEADER,
    )
    if r.status == 404:
        logger.info(
            f"Summoner with summoner id: {summoner_id} wasn't found in game. Status code {r.status}"
        )
        return None
    if r.status != 200:
        logger.warning(
            f"Couldn't retrieve summoner with summoner id: {summoner_id}. Status code {r.status}"
        )
        return None
    data = json.loads(r.data.decode("utf-8"))

    banned_champions: list[BannedChampion] = []
    for banned in data["bannedChampions"]:
        banned_champions.append(
            BannedChampion(
                banned["pickTurn"],
                banned["championId"],
                banned["teamId"],
            )
        )

    participants: list[CurrentGameParticipant] = []
    for participant in data["participants"]:
        perks = Perks(
            [perk_id for perk_id in participant["perks"]["perkIds"]],
            participant["perks"]["perkStyle"],
            participant["perks"]["perkSubStyle"],
        )
        participants.append(
            CurrentGameParticipant(
                participant["championId"],
                perks,
                participant["profileIconId"],
                participant["bot"],
                participant["teamId"],
                participant["summonerName"],
                participant["summonerId"],
                participant["spell1Id"],
                participant["spell2Id"],
            )
        )

    return GameInfo(
        data["gameId"],
        data["gameType"],
        data["gameStartTime"],
        data["mapId"],
        data["gameLength"],
        data["platformId"],
        data["gameMode"],
        banned_champions,
        data.get("gameQueueConfigId", None),
        data["observers"]["encryptionKey"],
        participants,
    )
