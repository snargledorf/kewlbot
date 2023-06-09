# kewlbot

Check the bot in [here](https://t.me/kewlcidsbot).

## Supported commands:
- `/boop` responds with a random dog picture or video
- `/carrot` responds with a random horse picture
- `/tips` responds with a random tip from /r/LifeProTips or /r/YouShouldKnow
- `/javi` responds with a javi
- `/midge` responds with a midge
- `/shrug` responds with a ¯\\\_(ツ)_/¯
- `/imagegen` send a prompt and a new image will be generated
  - Rate limit is stricter as this one will eventually cost money
- `/changelog` responds with latest CHANGELOG.md

### Adding photos/videos to a command
Additional photos or video can be added to commands by sending a photo or video and putting the command in the caption

### Subreddit name auto-linking
If a subreddit name is detected in a message, the bot will respond with a link to the subreddit.
- Only subreddit names in the /r/\<subname\> or r/\<subname\> format are recognized
- Multiple subreddit names in a message are supported and will be sent as seperate links
- Full reddit urls are ignored (IE. https://www.reddit.com/r/TelegramBots/)

# Requirements
- python 3
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [PRAW](https://github.com/praw-dev/praw)
- [OpenAI](https://github.com/openai/openai-python)
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) (Optional)

# Steps
1. Install dependancies
```
pip install -r requirements.txt
```

2. Set the required environment variables
``` 
TELEGRAM_BOT_TOKEN
OPENAI_API_KEY
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
