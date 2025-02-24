import asyncio
import json
import os
import re
import sys
import uuid
from datetime import timedelta

import psutil
from name_that_hash import check_hashes, hash_namer, hashes


# Random
def text(tag: str) -> str:
    texts = json.load(open("texts.json", "r", encoding="UTF-8"))
    return texts[tag]


def get_hashtype(hash: str) -> int | None:
    nth = hash_namer.Name_That_Hash(hashes.prototypes)
    checker = check_hashes.HashChecker({"verbose": 1, "file": None, "greppable": False, "base64": False, "accessible": False, "extreme": False, "no_banner": False, "no_john": False, "no_hashcat": False}, nth=nth)
    checker.single_hash(hash)
    try:
        return checker.output[0].get_prototypes()[0]["hashcat"]
    except IndexError:
        return None


def is_ip_address(text: str) -> bool:
    ip_pattern = re.compile(r"^(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\." r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\." r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\." r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$")
    return bool(ip_pattern.match(text))


# Hashcat
def is_hashcat_running() -> bool:
    executable_name = "hashcat.exe" if sys.platform == "win32" else "hashcat"

    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == executable_name:
            return True
    return False


async def dehash(hash: str) -> str | None:
    while is_hashcat_running():
        await asyncio.sleep(3)
    hashcat_dir = os.path.join("hashcat-6.2.6")
    hashcat_executable = os.path.join(hashcat_dir, "hashcat.exe")
    wordlist = os.path.join("rockyou.txt")
    unique_output = str(uuid.uuid4()) + ".txt"

    command = [hashcat_executable, "--potfile-disable", "-a", "0", "-m", str(get_hashtype(hash)), "-w", "4", "-d", "1", "-o", unique_output, hash, wordlist]
    process = await asyncio.create_subprocess_exec(*command, cwd=hashcat_dir)
    await process.communicate()

    try:
        filepath = os.path.join(hashcat_dir, unique_output)
        with open(filepath, "r") as f:
            password = f.readline().strip().split(":")[1]
        os.remove(filepath)
        return password
    except FileNotFoundError:
        return None


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
