import asyncio
import os
from datetime import datetime

from rich.progress import Progress, TaskID

import utils

config = utils.open_json("config.json")
progress_bar = Progress()
all_tokens = utils.count_tokens()
if all_tokens >= 1:
    progress = progress_bar.add_task("[red]Status: ", total=all_tokens)
start_time = datetime.now()
valid, invalid, phone_lock, nitro = utils.create_needed(start_time)
show_flags, show_guilds, check_nitro_credits, \
    check_payments, check_promotions, check_connections, \
    check_boosts, mask_tokens = config["show_flags"], \
    config["show_guilds"], config["check_nitro_credits"], \
    config["check_payments"], config["check_promotions"], \
    config["check_connections"], config["check_boosts"], \
    config["mask_tokens"]


async def check_token(token: str, prog: Progress, task: TaskID):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Alt-Used": "discord.com",
        "Authorization": token,
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cookie": "__dcfduid=8ae3ca90b4d911ec998447df76ccab6d; "
                  "__sdcfduid"
                  "=8ae3ca91b4d911ec998447df76ccab6d07a29d8ce7d96383bcbf0ff12d2f61052dd1691af72d9101442df895f59aa340; "
                  "OptanonConsent=isIABGlobal=false&datestamp=Tue+Sep+20+2022+15%3A55%3A24+GMT%2B0200+("
                  "hora+de+verano+de+Europa+central)&version=6.33.0&hosts=&landingPath=NotLandingPage&groups=C0001"
                  "%3A1%2CC0002%3A1%2CC0003%3A1&AwaitingReconsent=false&geolocation=ES%3BMD; "
                  "__stripe_mid=1798dff8-2674-4521-a787-81918eb7db2006dc53; "
                  "OptanonAlertBoxClosed=2022-04-15T16:00:46.081Z; _ga=GA1.2.313716522.1650038446; "
                  "_gcl_au=1.1.1755047829.1662931666; _gid=GA1.2.778764533.1663618168; locale=es-ES; "
                  "__cfruid=fa5768ee3134221f82348c02f7ffe0ae3544848a-1663682124",
        "Host": "discord.com",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/app",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    }
    if mask_tokens:
        masked_token = token.split(".")[-1].replace(token.split(".")[-1], "*" * len(token.split(".")[-1]))
        masked_token = f"{'.'.join(token.split('.')[:-1])}.{masked_token}"
    else:
        masked_token = token

    status, info = await utils.get_me(headers=headers)

    if status == 200:
        locale = None
        user_creation = (int(info["id"]) >> 22) + 1420070400000
        user_creation = datetime.fromtimestamp(user_creation / 1000.0)
        nitro_credits = 'Nitro classic/boost credits: Enable "check_nitro_credits" feature in config.json!\n'
        guilds_text, payments_text, \
            gifts_text, promotions_text, connections_text, \
            boosts_text = "--- guilds ---\n", "--- payments ---\n", \
            "--- gifts info ---\n", "--- promotions ---\n", \
            "--- account connections ---\n", "--- boosts ---\n"
        if "locale" in info:
            locale = info["locale"]

        flags = [
            [1 << 0, "Staff Team"],
            [1 << 1, "Guild Partner"],
            [1 << 2, "HypeSquad Events Member"],
            [1 << 3, "Bug Hunter Level 1"],
            [1 << 5, "Dismissed Nitro promotion"],
            [1 << 6, "House Bravery Member"],
            [1 << 7, "House Brilliance Member"],
            [1 << 8, "House Balance Member"],
            [1 << 9, "Early Nitro Supporter"],
            [1 << 10, "Team User"],
            [1 << 14, "Bug Hunter Level 2"],
            [1 << 16, "Verified Bot"],
            [1 << 17, "Early Verified Bot Developer"],
            [1 << 18, "Moderator Programs Alumni"],
            [1 << 19, "Bot uses only http interactions"],
            [1 << 22, "Active Developer"]
        ]
        flags_all = list()
        if show_flags:
            for i in range(len(flags)):
                if (info["public_flags"] & flags[i][0]) == flags[i][0]:
                    flags_all.append(flags[i][1])
        else:
            flags_all.append('Enable "show_flags" feature in config.json!')

        prog.update(task, advance=0.2)

        premium_type = "No nitro" \
            if info["premium_type"] == 0 \
            else "Nitro Classic" \
            if info["premium_type"] == 1 \
            else "Nitro Boost" if info["premium_type"] == 2 else "Nitro Basic"

        if premium_type != "No nitro":
            nitro_start, nitro_end = await utils.get_nitro_info(headers=headers)
        else:
            nitro_start, nitro_end = "No nitro", "No nitro"

        if check_nitro_credits:
            classic_credits, nitro_boost_credits = await utils.check_nitro_credit(headers=headers)
            nitro_credits = f"Nitro classic/boost credits: {classic_credits}/{nitro_boost_credits}\n"

        if check_nitro_credits:
            gifts = await utils.get_gifts(headers=headers)
            gifts_text += "".join(
                [f'{gift}\n' for gift in gifts]
            ) if len(gifts) >= 1 else 'No gifts in account\n'
        else:
            gifts_text += 'Gifts info: Enable "check_nitro_credits" feature in config.json!\n'

        prog.update(task, advance=0.2)

        if check_payments:
            payments = await utils.check_payments(headers=headers)
            payments_text += ''.join(
                [f'{payment}\n' for payment in payments]
            ) if len(payments) >= 1 else "No payments in account\n"
        else:
            payments_text += 'Payments: Enable "check_payments" feature in config.json!\n'

        prog.update(task, advance=0.1)

        if show_guilds:
            guilds = await utils.get_guilds(headers=headers)
            guilds_text += ''.join(
                [f"ID: {_id} | Name: {name} | Owner: {owner}\n" for _id, (name, owner) in guilds.items()]
            ) if len(guilds) >= 1 else "No guilds in account\n"
        else:
            guilds_text += 'Guilds info: Enable "show_guilds" feature in config.json!\n'

        prog.update(task, advance=0.1)

        if check_connections:
            connections = await utils.get_connections(headers=headers)
            connections_text += ''.join([
                f"Connection type: {conn_type} | Nickname: {name} | shows in profile: {sh_prof} |"
                f" Verified?: {verified} | Revoked: {revoked}\n"
                for conn_type, (name, sh_prof, verified, revoked) in connections.items()
            ]) if len(connections) >= 1 else "No connections in account\n"
        else:
            connections_text += 'Connections: Enable "check_connections" feature in config.json!\n'

        prog.update(task, advance=0.1)

        if check_promotions and locale is not None:
            promotions = await utils.get_promotions(headers=headers, locale=locale)  # type: ignore
            promotions_text += ''.join([
                f"Promo: {name} | Start time: {s_time} | End time: {end_time} |"
                f" Link to activate: {link} | Code: {code}\n"
                for name, (s_time, end_time, link, code) in promotions.items()
            ]) if len(promotions) >= 1 else "No promotions in account\n"
        else:
            promotions_text += 'Promotions: Enable "check_promotions" feature in config.json!\n'

        prog.update(task, advance=0.1)

        if check_boosts:
            boosts = await utils.check_boosts(headers=headers)
            boosts_text += ''.join([
                f"Boost status: {boost_status} | Guild id: {guild_id} | Boost id: {boost_id} "
                f"| ended: {ended} | canceled: {canceled} | Cooldown ends: {cooldown_end}\n"
                for boost_id, (guild_id, ended, boost_status, canceled, cooldown_end, subscription_id) in boosts.items()
            ]) if len(boosts) >= 1 else "No boosts in account\n"
        else:
            boosts_text += 'Boosts info: Enable "check_boosts" feature in config.json!\n'

        prog.update(task, advance=0.1)

        username = info["username"]
        full_name = f"{info['username']}#{info['discriminator']}"
        avatar = f"https://cdn.discordapp.com/avatars/{info['id']}/{info['avatar']}." \
                 f"{'gif' if str(info['avatar']).startswith('a_') else 'png'}" if info["avatar"] else None
        banner = f"https://cdn.discordapp.com/banners/{info['id']}/{info['banner']}." \
                 f"{'gif' if str(info['banner']).startswith('a_') else 'png'}" if info["banner"] else None
        email = info["email"]
        phone = info["phone"]
        verified = info["verified"]
        mfa = info["mfa_enabled"]
        bio = info["bio"] if info["bio"] else None
        user_id = info["id"]

        text = f"""
token {masked_token} is valid
-------
username: {username}
ID: {user_id}
Full Name: {full_name}
bio: {bio}
locale: {locale if locale is not None else 'cannot fetch account locale'}

---- URLs ----
avatar URL: {avatar}
banner URL: {banner}

---- other info ----
email: {email}
email is verified? {verified}
phone: {phone}
MFA? {mfa}
created at: {utils.from_datetime_to_humanly(user_creation)}

---- Nitro & Payments ----
Nitro: {premium_type}
Nitro started: {nitro_start}
Nitro ends: {nitro_end}
{f"Flags: {', '.join(flags_all)}"}
{nitro_credits}
{guilds_text}
{payments_text}
{gifts_text}
{promotions_text}
{connections_text}
{boosts_text}"""
        await utils.custom_print(text=text, color="info", print_=True, write_file=True, file=valid)
        if premium_type != "No nitro":
            await utils.custom_print(text=text, write_file=True, file=nitro)
        prog.update(task, advance=0.2)
    elif status == 401:
        await utils.custom_print(f"token {masked_token} invalid!", color="error",
                                 print_=True, write_file=True, file=invalid)
        prog.update(task, advance=1)
    elif status == 403:
        await utils.custom_print(f"token {masked_token} phone locked!", color="error",
                                 print_=True, write_file=True, file=phone_lock)
        prog.update(task, advance=1)
    elif status == 429:
        await utils.custom_print("Rate Limit", color="error", print_=True)
        prog.update(task, advance=1)
    return


async def main():
    tasks = []
    tokens = await utils.get_tokens()
    with progress_bar:
        for token in tokens:
            tasks.append(asyncio.ensure_future(asyncio.shield(check_token(token, progress_bar, progress))))
            await asyncio.sleep(0.3)

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    os.system("clear" if os.name != "nt" else "cls")
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
