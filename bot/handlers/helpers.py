import json
import re
from datetime import timedelta

from name_that_hash import check_hashes, hash_namer, hashes


# Random
def text(tag: str) -> str:
    texts = json.load(open("config/texts.json", "r", encoding="UTF-8"))
    return texts[tag]


def convert_authme_sha256(authme_hash) -> str:
    if not authme_hash.startswith("$SHA$"):
        raise ValueError("Invalid AuthMe hash format")

    parts = authme_hash.split("$")
    if len(parts) != 4:
        raise ValueError("Malformed AuthMe hash")

    salt, hash_value = parts[2], parts[3]
    return f"$dynamic_82${hash_value}${salt}"


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
