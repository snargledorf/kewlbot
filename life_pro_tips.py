import asyncpraw
import re

async def get_random_lpt():
    async with asyncpraw.Reddit('telegrambot', user_agent = 'telegrambot:telegram.lpt.bot:1.0.0') as reddit:
        subreddits = await reddit.subreddit('lifeprotips+youshouldknow')
        while True:
            submission = await subreddits.random()
            if not re.search('request', submission.title, re.IGNORECASE):
                
                lpt = LPT()
                lpt.title = submission.title

                if submission.is_self:
                    lpt.type = 'text'
                    lpt.content = submission.selftext
                    
                lpt.permalink = 'https://reddit.com' + submission.permalink

                return lpt


class LPT():
    type=""
    title=""
    content=""
    permalink=""