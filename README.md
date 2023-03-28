# kewlbot

Check the bot in [here](https://t.me/kewlcidsbot).

## Supported commands:
- `/boop` responds with a random dog picture or video
- `/carrot` responds with a random horse picture
- `/tips` responds with a random tip from /r/LifeProTips or /r/YouShouldKnow
- `/javi` responds with a javi
- `/midge` responds with a midge
- `/shrug` responds with a ¯\\\_(ツ)_/¯

### Adding photos/videos to a command
Additional photos or video can be added to commands by sending a photo or video and putting the command in the caption

# Requirements
- python 3
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [PRAW](https://github.com/praw-dev/praw)
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) (Optional)

# Steps
1. Install the library.
```
pip install python-telegram-bot
pip install praw
```

2. Create a my_secrets.py
``` python
telegram_bot_token = '<bot_token>'
```

3. Create a praw.ini

### Example:
``` ini
[DEFAULT]
# A boolean to indicate whether or not to check for package updates.
check_for_updates=True

# Object to kind mappings
comment_kind=t1
message_kind=t4
redditor_kind=t2
submission_kind=t3
subreddit_kind=t5
trophy_kind=t6

# The URL prefix for OAuth-related requests.
oauth_url=https://oauth.reddit.com

# The amount of seconds of ratelimit to sleep for upon encountering a specific type of 429 error.
ratelimit_seconds=5

# The URL prefix for regular requests.
reddit_url=https://www.reddit.com

# The URL prefix for short URLs.
short_url=https://redd.it

# The timeout for requests to Reddit in number of seconds
timeout=16

[telegrambot]
client_id=<client_id>
client_secret=<client_secret>
```

3. Run the program.
```
python main.py
```

4. (Optional) Compile using pyinstaller
```
pyinstaller .\main.spec
```
```
python -m PyInstaller .\main.spec
