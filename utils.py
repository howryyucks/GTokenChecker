import os
from datetime import datetime
from re import findall
from typing import Union, Literal, Any, Coroutine, AsyncGenerator

import aiofiles
from aiohttp import ClientSession
from ujson import load

pattern = r"\b[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
BASE_URL = "https://discord.com/"


def open_json(filename: str = "config.json"):
    return load(open(filename, "r"))


config = open_json()


class ProgramError(Exception):
    def __init__(self, *args):
        super(ProgramError, self).__init__(*args)


async def custom_print(
        text: str,
        color: Literal["info", "debug", "error", "warn"] = "warn",
        print_: bool = False,
        write_file: bool = False,
        file: str = None,
) -> None:
    colors = {
        "info": f"\033[1;32;48m{text}\033[1;37;0m ",
        "debug": f"\033[1;34;48m{text}\033[1;37;0m",
        "error": f"\033[1;31;48m{text}\033[1;37;0m",
        "warn": f"\033[1;33;48m{text}\033[1;37;0m ",
    }
    if print_:
        print(colors[color])
    if write_file and file:
        await write_to_file(info=text, file=file)
    return colors[color]


def count_tokens() -> int:
    with open("tokens.txt", "r", errors="ignore") as file:
        lines = file.read()
    token_ = findall(pattern, lines)
    return len(token_)


def gen_parse_token(tokens: str) -> tuple:
    token_ = findall(pattern, tokens)
    if len(token_) >= 1:
        for token in token_:
            yield token, len(token_)
    else:
        print("Please, input tokens in tokens.txt!")
        exit(0)


def from_datetime_to_humanly(date: datetime,
                             to_string: Union[datetime.strptime, str] = "%d.%m.%Y %H:%M:%S") -> str:
    return date.strftime(to_string)


def from_iso_format_to_humanly(iso: str, to_string: Union[datetime.strptime, str] = "%d.%m.%Y %H:%M:%S"):
    date = datetime.fromisoformat(iso)
    return date.strftime(to_string)


async def get_tokens() -> AsyncGenerator[tuple[str, int], Any]:
    if not os.path.exists("tokens.txt"):
        raise ProgramError("please, create tokens.txt file!!")
    async with aiofiles.open("tokens.txt", "r", errors="ignore") as file:
        lines = await file.read()
    for token, all_tokens in gen_parse_token(lines):
        yield token, all_tokens


async def write_to_file(info: str, file: str):
    if config["write_tokens_to_file"]:
        async with aiofiles.open(file, "a+", encoding="utf-8", errors="ignore") as file:
            await file.write(f"{info}\n")
        return


async def check_nitro_credit(headers: dict) -> tuple[int, int]:
    dict_credits = {"classic_credits": 0, "boost_credits": 0}
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/applications/521842831262875670/entitlements?exclude_consumed=true",
                               headers=headers) as response:
            if response.status == 200:
                text = await response.text()
                dict_credits["classic_credits"] = text.count("Nitro Classic")
                dict_credits["boost_credits"] = text.count("Nitro Monthly")

    return dict_credits["classic_credits"], dict_credits["boost_credits"]


async def check_payments(headers: dict):
    cc_digits = {"american express": "3", "visa": "4", "mastercard": "5"}
    account_cards = []
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/billing/payment-sources", headers=headers) as response:
            if response.status == 200:
                search_billing = await response.json()
                for grab in search_billing:
                    grab1 = grab["billing_address"]
                    if grab["type"] == 1:
                        cc_brand = grab["brand"]
                        cc_first = cc_digits.get(cc_brand)
                        cc_last = grab["last_4"]
                        cc_month = str(grab["expires_month"])
                        cc_year = str(grab["expires_year"])
                        card = f"""
Payment Type: Credit card
Valid: {not grab["invalid"]}
CC Holder Name: {grab1["name"]}
CC Brand: {cc_brand.title()}
CC Number: {''.join(z if (i + 1) % 2 else f'{z} ' for i, z in
                    enumerate((cc_first if cc_first else '*')
                              + ('*' * 11) + cc_last))}
CC Date: {(f'0{cc_month}' if len(cc_month) < 2 else cc_month) + '/' + cc_year[2:4]}
Address 1: {grab1["line_1"]}
Address 2: {grab1["line_2"] if grab1["line_2"] else ''}
City: {grab1["city"]}
Postal code: {grab1["postal_code"]}
State: {grab1["state"] if grab1["state"] else ''}
Country: {grab1["country"]}
Default Payment Method: {grab['default']}\n"""
                    elif grab["type"] == 2:
                        card = f"""
Payment Type: PayPal
Valid: {not grab['invalid']}
PayPal Name: {grab1["name"]}
PayPal Email: {grab['email']}
Address 1: {grab1["line_1"]}
Address 2: {grab1["line_2"] if grab1["line_2"] else ''}
City: {grab1["city"]}
Postal code: {grab1["postal_code"]}
State: {grab1["state"] if grab1["state"] else ''}
Country: {grab1["country"]}
Default Payment Method: {grab['default']}\n"""
                    account_cards.append(card)
    return account_cards


async def get_guilds(headers: dict):
    guilds: dict[str, list[str]] = {}
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v9/users/@me/guilds?with_counts=true", headers=headers) as response:
            if response.status == 200:
                r_json = await response.json()
                for guild in r_json:
                    _id = guild["id"]
                    name = guild["name"]
                    owner = guild["owner"]
                    guilds[_id] = [name, owner]
    return guilds


async def get_gifts(headers: dict):
    gifts = []
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/entitlements/gifts", headers=headers) as response:
            if response.status == 200:
                r_json = await response.json()
                for gift in r_json:
                    gifts.append(gift['subscription_plan']['name'])
    return gifts


async def get_me(headers: dict) -> Union[Coroutine[Any, Any, None], dict, None, tuple[int, str]]:
    info = None
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me", headers=headers) as response:
            if response.status == 200:
                info = await response.json()
            elif response.status == 401:
                return response.status, ""
            elif response.status == 403:
                return response.status, ""

    return response.status, info


async def get_connections(headers: dict) -> dict:
    connections = {}
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/connections", headers=headers) as response:
            if response.status == 200:
                info = await response.json()

    for connection in info:
        connection_type = connection["type"]
        name = connection["name"]
        shows_in_profile = connection["visibility"] == 1
        verified = connection["verified"]
        revoked = connection["revoked"]

        connections[connection_type] = [name, shows_in_profile, verified, revoked]

    return connections


async def get_promotions(headers: dict, locale: str) -> dict:
    promo_ = {}
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get(
                f"/api/v10/users/@me/outbound-promotions/codes?locale={locale}",
                headers=headers
        ) as response:
            if response.status == 200:
                res = await response.json()

    # print(res)
    for result in res:
        name = result["promotion"]["outbound_title"]
        start_time = from_iso_format_to_humanly(result["promotion"]["start_date"])
        end_time = from_iso_format_to_humanly(result["promotion"]["end_date"])
        link_to = result["promotion"]["outbound_redemption_page_link"]
        code = result["code"]

        promo_[name] = [start_time, end_time, link_to, code]

    return promo_


async def check_boosts(headers: dict) -> dict:
    boosts = {}
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/guilds/premium/subscription-slots", headers=headers) as response:
            info = await response.json()

    for boost_info in info:
        boost_id = boost_info["id"]
        guild_id, ended = "Unused boost", False
        subscription_id = boost_info["subscription_id"]
        if boost_info["premium_guild_subscription"].get("guild_id", False) is not False:
            guild_id = boost_info["premium_guild_subscription"]["guild_id"]
            ended = boost_info["premium_guild_subscription"]["ended"]
            boost_status = "Used"
        else:
            boost_status = "Unused"
        canceled = boost_info["canceled"]
        cooldown_ends_at = "No cooldown" \
            if boost_info["cooldown_ends_at"] is None \
            else from_iso_format_to_humanly(boost_info["cooldown_ends_at"])

        boosts[boost_id] = [guild_id, ended, boost_status, canceled, cooldown_ends_at, subscription_id]

    return boosts


async def get_nitro_end(headers: dict) -> str:
    nitro_end = None

    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/billing/subscriptions", headers=headers) as resp:
            if resp.status == 200:
                nitro_billing = await resp.json()
                if nitro_billing:
                    dt = datetime.fromisoformat(nitro_billing[0]["current_period_end"])
                    nitro_end = from_datetime_to_humanly(date=dt)

    return nitro_end


def create_needed(time: datetime):
    if config["write_tokens_to_file"]:
        files = ["valid_tokens.txt", "invalid_tokens.txt", "phonelock_tokens.txt", "nitro_tokens.txt"]
        res = from_datetime_to_humanly(date=time, to_string='%d.%m.%Y %H_%M_%S')
        os.makedirs(f"results/result-{res}")

        for file in files:
            with open(f"results/result-{res}/{file}", "w"):
                pass

        return f"results/result-{res}/{files[0]}", f"results/result-{res}/{files[1]}", \
            f"results/result-{res}/{files[2]}", f"results/result-{res}/{files[3]}"
    else:
        return None, None, None, None
