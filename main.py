import os
import re
import aiofiles
import aiohttp

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ApplicationHandlerStop
from telegram.ext.filters import Caption, PHOTO, VIDEO, Regex
from telegram.helpers import escape_markdown

from life_pro_tips import get_random_lpt
import MediaApi

from datetime import datetime
from bs4 import BeautifulSoup
    
changelog_file_path = 'CHANGELOG.md'

subreddit_regex = r'(?:^|\s)\/?[r]\/(\w+)\b'
hahaa_regex = r'[Hh]a [Hh]aa+\!?'

image_extensions = ['.jpg','.jpeg','.png']
video_extensions = ['.mp4','.gif', '.mov']

# (Basic) Rate limiting
max_tickets_per_term = 10
term_length_minutes = 10
current_term_start_time = datetime.now()
current_tickets_count = 0

def get_telegram_bot_token():
    return os.environ['TELEGRAM_BOT_TOKEN']

def is_debug_mode():
    return 'VSCODE_DEBUG_MODE' in os.environ and os.environ['VSCODE_DEBUG_MODE'] == "true"

def get_media_subdir_path(subdir):
    return get_media_dir_path() + f'/{subdir}/'

def get_media_dir_path():
    if 'KEWLBOT_MEDIA_FOLDER' in os.environ:
        return os.environ['KEWLBOT_MEDIA_FOLDER']
    return 'media'

def try_take_ticket():
    global current_term_start_time, current_tickets_count

    if is_debug_mode():
        return True

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
    return os.path.splitext(url)[-1].lower()

async def get_random_horse_picture_url():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://generatorfun.com/random-horse-image') as response:
            htmltext = await response.read()
            soup = BeautifulSoup(htmltext, 'html.parser')
            horse_image_relative_url = soup.select_one('body > main > div > img')['src']
            return "https://generatorfun.com/" + horse_image_relative_url

async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if try_take_ticket() is False:
        await send_rate_limit_response(update, context)
        return
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Finding you a helpful tip...')
        
    lpt = await get_random_lpt()
    message = f"""*[{escape_markdown(lpt.title, 2)}]({lpt.permalink})*

{escape_markdown(lpt.content, 2)}"""
    
    if len(message) > 1000:
        message = message[:977] + '\.\.\.'

    await context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='MarkdownV2', text=message)

async def shrug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('¯\_(ツ)_/¯')

async def boop(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    await send_random_media(boop_api, update, context)

async def carrot(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    await send_random_media(carrot_api, update, context)

async def javi(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    await send_random_media(javi_api, update, context)

async def get_javi_meme_url():
    return 'https://media.tenor.com/iEaaKez7nDcAAAAC/smiling-javi-gutierrez.gif'

async def midge(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    await send_random_media(midge_api, update, context)

async def hahaa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_random_media(hahaa_api, update, context)

async def subreddit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subreddit_name_matches = re.finditer(subreddit_regex, update.message.text)
    for subreddit_name_match in subreddit_name_matches:
        subreddit_name = subreddit_name_match.group(1)
        await update.message.reply_text(f'https://www.reddit.com/r/{subreddit_name}/')

async def changelog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiofiles.open(changelog_file_path, mode='r') as changelog_file:
        changelog_contents = await changelog_file.read(1000)

    if len(changelog_contents) == 1000:
        changelog_contents = changelog_contents[:997] + '\.\.\.'

    await update.message.reply_text(changelog_contents)
                                   
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! If you /boop me, I'll send you a cute doggo!")

async def addCommandMedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file=None
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
    else:
        file = await update.message.video.get_file()

    download_folder_path = get_media_dir_path() + update.message.caption + '/'
    if not os.path.exists(download_folder_path):
        os.mkdir(download_folder_path)

    download_file_path = download_folder_path + file.file_unique_id + os.path.splitext(file.file_path)[-1]
    if os.path.exists(download_file_path):
        raise ApplicationHandlerStop()

    await file.download_to_drive(download_file_path)

    await update.message.reply_text('New media added for ' + update.message.caption)
    raise ApplicationHandlerStop()

async def send_random_media(media_retriever: MediaApi.MediaRetriever, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if try_take_ticket() is False:
        await send_rate_limit_response(update, context)
        return
    
    file = await media_retriever.get_random_media()

    file_extension = get_file_extension(file)   
    chat_id = update.effective_chat.id

    if file_extension in image_extensions:
        await context.bot.send_photo(chat_id=chat_id, photo=file)
    elif file_extension in video_extensions:
        await context.bot.send_video(chat_id=chat_id, video=file)

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
    CommandHandler('midge', midge),
    CommandHandler('shrug', shrug),
    CommandHandler('changelog', changelog),
    MessageHandler(Regex(hahaa_regex), hahaa),
    MessageHandler(Regex(subreddit_regex), subreddit)
]

boop_api = MediaApi.MultiMediaRetriever([MediaApi.ApiRoutineMediaRetrieve(get_random_dog_url), MediaApi.LocalFileMediaRetriever(get_media_subdir_path('boop'))])
carrot_api = MediaApi.MultiMediaRetriever([MediaApi.ApiRoutineMediaRetrieve(get_random_horse_picture_url, 15), MediaApi.LocalFileMediaRetriever(get_media_subdir_path('carrot'))])
javi_api = MediaApi.MultiMediaRetriever([MediaApi.ApiRoutineMediaRetrieve(get_javi_meme_url, 0), MediaApi.LocalFileMediaRetriever(get_media_subdir_path('javi'))])
midge_api = MediaApi.LocalFileMediaRetriever(get_media_subdir_path('midge'))
hahaa_api = MediaApi.LocalFileMediaRetriever(get_media_subdir_path('hahaa'))

if __name__ == '__main__':
    print(f'Media folder: {get_media_dir_path()}')
    application = ApplicationBuilder().token(get_telegram_bot_token()).build()    
    application.add_handlers(commands)    
    application.run_polling()
