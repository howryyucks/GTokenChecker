# GToken_Checker

[gitlab version](https://gitlab.com/snaky1/gtoken-checker)

Simple token checker

# Features

- Checks token in threads
- Checks public flags, nitro (type, end)
- Checks nitro credits
- Checks credit cards

# Installation

- Download python from [python.org site](https://python.org)
- Download this checker and extract it
- Type cmd.exe and go to directory with project
- Type `pip install -r requirements.txt` to install needed packages
- Put tokens into tokens.txt
- Customize the `config.json` file to your needs
- Run the program (`python main.py`)

# TODO

- [x] Check nitro credits if available in account
- [x] Check credit cards in account
- [ ] Show billing history
- [x] Check guilds (all guilds or with admin permissions)
- [ ] Show relationships (friends in account)
- [ ] Show DMs (count of DMs)
- [x] Advanced config
- [x] Progress bar
- [x] Sort tokens
- [x] Outbound-promotions
- [ ] Account connections
- [ ] Check boosts in account

# What's New

0.1.3:

**Now, GTokenChecker checks:**
-
- Boosts in account
- Promotions (promo codes like Xbox Game Pass)
- Account connections



0.1.2:

- Advanced configuration in `config.json`
- Now all tokens (valid, invalid, phone_lock, nitro) will be sorted in results.

Structure on the `results` folder:

- result-date_of_program_started
    - invalid_tokens.txt
    - nitro_tokens.txt
    - phonelock_tokens.txt
    - valid_tokens.txt
-
- Added progress bar to show percent of completed
