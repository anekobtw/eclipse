import re

from name_that_hash import check_hashes, hash_namer, hashes

from enums import Databases


# Random
def get_hashtype(hash: str):
    nth = hash_namer.Name_That_Hash(hashes.prototypes)
    checker = check_hashes.HashChecker({"verbose": 1, "file": None, "greppable": False, "base64": False, "accessible": False, "extreme": False, "no_banner": False, "no_john": False, "no_hashcat": False}, nth=nth)
    checker.single_hash(hash)
    try:
        return checker.output[0].get_prototypes()
    except IndexError:
        return None


def is_ip_address(text: str) -> bool:
    pattern = re.compile(
        r'^'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
        r'$'
    )
    return bool(pattern.match(text))


def get_all_time_searched() -> int:
    searched = 0
    for user in Databases.USERS.value.get_all():
        searched += user[2]
    return searched
