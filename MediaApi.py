import os
import random
import asyncio

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

class MediaRetriever():
    
    image_extensions = ['.jpg','.jpeg','.png']
    video_extensions = ['.mp4','.gif']

    recent_media = []

    def __init__(self, command_name, api_coroutine=None, recent_media_max=5):
        self.command_name = command_name
        self.api_coroutine = api_coroutine
        self.recent_media_max = recent_media_max

    async def send_random_media_for_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file = await self.get_random_media_for_command()
        file_extension = self.get_file_extension(file)    
        chat_id = update.effective_chat.id

        if file_extension in self.image_extensions:
            await context.bot.send_photo(chat_id=chat_id, photo=file)
        elif file_extension in self.video_extensions:
            await context.bot.send_video(chat_id=chat_id, video=file)

    async def get_random_media_for_command(self):
        get_media_method = self.determine_get_media_method()
        file = await get_media_method()

        recent_media_count = self.recent_media_max
        if not self.api_coroutine:
            recent_media_count = min(self.get_command_local_file_count()/self.recent_media_max, recent_media_count)

        while len(self.recent_media) > recent_media_count:
            self.recent_media.pop()

        while file in self.recent_media:
            get_media_method = self.determine_get_media_method()
            file = await get_media_method()
        
        self.recent_media.append(file)

        return file

    def determine_get_media_method(self):
        get_media_method = None
        if (not self.api_coroutine or self.should_try_pull_from_local()) and self.command_has_local_files():
            get_media_method = lambda: self.get_random_local_file_for_command()
        else:
            get_media_method = self.api_coroutine
        
        if not get_media_method:
            raise ApplicationHandlerStop()
        
        return asyncio.coroutine(get_media_method)

    def command_has_local_files(self):
        return self.get_command_local_file_count() > 0

    def get_command_local_file_count(self):
        if not os.path.exists(self.get_media_folder_path()):
            return 0
        
        media_folder = self.get_media_folder_path()
        return len(os.listdir(media_folder))

    def should_try_pull_from_local(self):
        return random.randint(0, 1)==1

    def get_random_local_file_for_command(self):
        media_folder = self.get_media_folder_path()
        files = os.listdir(media_folder)
        return media_folder + files[random.randint(0, len(files)-1)]
    
    def get_file_extension(self, filename):
        return os.path.splitext(filename)[-1]
    
    def get_media_folder_path(self):
        return 'media/' + self.command_name + '/'