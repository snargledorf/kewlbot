from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.helpers import escape_markdown
import aiohttp
import re
import my_secrets
from life_pro_tips import get_random_lpt
from datetime import datetime

image_extensions = ['jpg','jpeg','png']
video_extensions = ['mp4','gif']

# (Basic) Rate limiting
max_tickets_per_term = 10
term_length_minutes = 10
current_term_start_time = datetime.now()
current_tickets_count = 0

def try_take_ticket():
    global current_term_start_time, current_tickets_count

    # Check if we have moved on to the next term
    current_term_length = datetime.now() - current_term_start_time

    if current_term_length.total_seconds() > (term_length_minutes*60):
        current_tickets_count = 0
        current_term_start_time = datetime.now()

    if (current_tickets_count is max_tickets_per_term):
        return False
    
    current_tickets_count+=1
    return True

async def get_url():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://random.dog/woof.json') as response:
            respJson = await response.json();
            return respJson['url']

async def get_media_url():
    file_extension = ''
    while file_extension not in image_extensions and file_extension not in video_extensions:
        url = await get_url()
        file_extension = get_file_extension(url)
    return url

def get_file_extension(url):
    return re.search("([^.]*)$",url).group(1).lower()

async def boop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if try_take_ticket() is False:
        await send_rate_limit_response(update, context)
        return

    url = await get_media_url()
    chat_id = update.effective_chat.id
    
    file_extension = get_file_extension(url)
    if file_extension in image_extensions:
        await context.bot.send_photo(chat_id=chat_id, photo=url)
    elif file_extension in video_extensions:
        await context.bot.send_video(chat_id=chat_id, video=url)

async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if try_take_ticket() is False:
        await send_rate_limit_response(update, context)
        return
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Finding you a helpful tip...')
        
    lpt = await get_random_lpt()
    message = """*[{}]({})*

{}""".format(escape_markdown(lpt.title, 2), lpt.permalink, escape_markdown(lpt.content, 2))
    
    if len(message) > 1000:
        message = message[:977] + '\.\.\.'

    await context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='MarkdownV2', text=message)
                                   
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! If you /boop me, I'll send you a cute doggo!")

async def send_rate_limit_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_term_length = datetime.now() - current_term_start_time
    time_left = int((term_length_minutes*60) - current_term_length.total_seconds())

    minutes, seconds = divmod(time_left, 60)
    
    time_left_str = ''
    if minutes != 0:
        time_left_str += '{} minute'.format(minutes)
        if minutes > 1:
            time_left_str += 's'
        
        time_left_str += ' and '

    time_left_str += '{} second'.format(seconds)
    if seconds > 1:
        time_left_str += 's'

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Woah, slow down! You can use me again in {}.".format(time_left_str))

if __name__ == '__main__':
    application = ApplicationBuilder().token(my_secrets.telegram_bot_token).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    boop_handler = CommandHandler('boop', boop)
    application.add_handler(boop_handler)

    tits_handler = CommandHandler('tips', tips)
    application.add_handler(tits_handler)
    
    application.run_polling()
