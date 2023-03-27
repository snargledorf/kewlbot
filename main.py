import os

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ApplicationHandlerStop
from telegram.ext.filters import Caption, PHOTO, VIDEO
from telegram.helpers import escape_markdown

import aiohttp

import my_secrets
from life_pro_tips import get_random_lpt
from MediaApi import MediaRetriever

from datetime import datetime
from bs4 import BeautifulSoup

image_extensions = ['.jpg','.jpeg','.png']
video_extensions = ['.mp4','.gif']

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

async def get_random_dog_api_url():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://random.dog/woof.json') as response:
            respJson = await response.json();
            return respJson['url']

async def get_random_dog_url():
    file_extension = ''
    while file_extension not in image_extensions and file_extension not in video_extensions:
        url = await get_random_dog_api_url()
        file_extension = get_file_extension(url)
    return url

def get_file_extension(url):
    return os.path.splitext(url)[-1]

async def get_random_horse_picture_url():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://generatorfun.com/random-horse-image') as response:
            htmltext = await response.read()
            soup = BeautifulSoup(htmltext, 'html.parser')
            horse_image_relative_url = soup.select_one('body > main > div > img')['src']
            return "https://generatorfun.com/" + horse_image_relative_url

async def boop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if try_take_ticket() is False:
        await send_rate_limit_response(update, context)
        return
    
    await boop_api.send_random_media_for_command(update, context)

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

async def carrot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if try_take_ticket() is False:
        await send_rate_limit_response(update, context)
        return
    
    await carrot_api.send_random_media_for_command(update, context)

async def javi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if try_take_ticket() is False:
        await send_rate_limit_response(update, context)
        return
    
    await javi_api.send_random_media_for_command(update, context)

async def midge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if try_take_ticket() is False:
        await send_rate_limit_response(update, context)
        return
    
    await midge_api.send_random_media_for_command(update, context)
                                   
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! If you /boop me, I'll send you a cute doggo!")

async def addCommandMedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file=''
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
    else:
        file = await update.message.video.get_file()

    download_folder_path = get_media_folder_path(update.message.caption[1:])
    if not os.path.exists(download_folder_path):
        os.mkdir(download_folder_path)

    download_file_path = download_folder_path + file.file_unique_id + os.path.splitext(file.file_path)[-1]
    if os.path.exists(download_file_path):
        raise ApplicationHandlerStop()

    await file.download_to_drive(download_file_path)
    raise ApplicationHandlerStop()

def get_media_folder_path(command_name):
    return 'media/' + command_name + '/'

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

commands = [
    CommandHandler('start', start),
    MessageHandler(Caption(['/boop', '/carrot', '/javi', '/midge']) & (PHOTO | VIDEO), addCommandMedia),
    CommandHandler('boop', boop),
    CommandHandler('carrot', carrot),
    CommandHandler('tips', tips),
    CommandHandler('javi', javi),
    CommandHandler('midge', midge)
]

boop_api = MediaRetriever('boop', get_random_dog_url)
carrot_api = MediaRetriever('carrot', get_random_horse_picture_url)
javi_api = MediaRetriever('javi', lambda: 'https://media.tenor.com/iEaaKez7nDcAAAAC/smiling-javi-gutierrez.gif', 0)
midge_api = MediaRetriever('midge')

if __name__ == '__main__':
    application = ApplicationBuilder().token(my_secrets.telegram_bot_token).build()
    
    application.add_handlers(commands)
    
    application.run_polling()
