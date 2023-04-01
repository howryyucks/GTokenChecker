# GToken_Checker

[gitlab version](https://gitlab.com/snaky1/GTokenChecker)

Simple token checker

# Features

- **Asynchronous support**
- **Check public flags, nitro (type, end), nitro credits, credit cards, boosts, promotions, account connections**

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
- [x] Show relationships (friends in account)
- [x] Show DMs (count of DMs)
- [x] Advanced config
- [x] Progress bar
- [x] Sort tokens
- [x] Outbound-promotions
- [x] Account connections
- [x] Check boosts in account

# What's New

### 0.1.4

- Add type hints in all functions
- Now, program checks private channels
- Removed `ujson` module from requirements.txt

### 0.1.3-2

- Fixed bug with fetching badges in account

### 0.1.3-1 (Bug-Fix)

- Fixed error in boosts

### 0.1.3:

#### Now, GTokenChecker checks:

- Boosts in account
- Promotions (promo codes like Xbox Game Pass)
- Account connections

### 0.1.2:

- Advanced configuration in `config.json`
- Now all tokens (valid, invalid, phone_lock, nitro) will be sorted in results.

Structure on the `results` folder:

- result-date_of_program_started
    - invalid_tokens.txt
    - nitro_tokens.txt
    - phonelock_tokens.txt
    - valid_tokens.txt

- Added progress bar to show percent of completed

### License: GNU GPL 3
