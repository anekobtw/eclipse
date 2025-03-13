import json
import re
from datetime import timedelta

from name_that_hash import check_hashes, hash_namer, hashes

from db import UsersDatabase

ud = UsersDatabase()


# Random
def text(tag: str) -> str:
    texts = json.load(open("config/texts.json", "r", encoding="UTF-8"))
    return texts[tag]


def get_hashtype(hash: str) -> int | None:
    nth = hash_namer.Name_That_Hash(hashes.prototypes)
    checker = check_hashes.HashChecker({"verbose": 1, "file": None, "greppable": False, "base64": False, "accessible": False, "extreme": False, "no_banner": False, "no_john": False, "no_hashcat": False}, nth=nth)
    checker.single_hash(hash)
    try:
        return checker.output[0].get_prototypes()
    except IndexError:
        return None


def is_ip_address(text: str) -> bool:
    ip_pattern = re.compile(r"^(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\." r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\." r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\." r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$")
    return bool(ip_pattern.match(text))


def parse_duration(duration_str) -> timedelta:
    match = re.match(r"(\d+)([dwm])", duration_str)
    if not match:
        raise ValueError("Invalid duration format")

    num, unit = int(match.group(1)), match.group(2)

    if unit == "d":
        return timedelta(days=num)
    elif unit == "w":
        return timedelta(weeks=num)
    elif unit == "m":
        return timedelta(days=num * 30)
    else:
        raise ValueError("Unsupported duration unit")

def get_quota_max(user_id: int) -> int:
    user = ud.get_user(user_id)
    base_quota = {"free": 5, "premium": 20, "premium+": 100}[user.subscription]
    
    invite_bonus = 0
    for invite, bonus in {3:5, 10:10, 20:15, 30:20, 50:35, 100:50}.items():
        if user.invited >= invite:
            invite_bonus = bonus

    return base_quota + invite_bonus


def get_progressbar(user_id: int):
    user = ud.get_user(user_id)
    invited = user.invited
    
    goals = [3, 10, 20, 30, 50, 100]
    next_goal = next(goal for goal in goals if invited < goal)
    
    progress = (invited / next_goal) * 100
    progress_bar_length = 20 
    progress_bar = "■" * int(progress / 100 * progress_bar_length)
    remaining = "□" * (progress_bar_length - len(progress_bar))
  
    return f"{progress_bar}{remaining} {invited}/{next_goal} ({int(progress)}%)"
