# Twitter to Misskey Avatar and Banner changer
### This was made to compliment and maybe in the future, replace https://github.com/aruriku/misskeyRSSbot
### It uses the twikit library to fetch the avatar and banner of a twitter user and upload it to a mirror on Misskey.

### Dependencies
- Python
- Everything in requirements.txt

### Setup
**You will need:** 
- a cookies.json file (for now you can make one using twikit, in the future there will be an interactive script to simplify it)
- a way to set your preferences
  - .env file with `AUTH_TOKEN`, `URL`, and `USER` set.
  - Environment variables set using docker(see docker-compose.yml) or your shell.
 
### Running
run with docker-compose or `python main.py`
