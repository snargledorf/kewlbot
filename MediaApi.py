import os
import random
import asyncio

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop
    
image_extensions = ['.jpg','.jpeg','.png']
video_extensions = ['.mp4','.gif', '.mov']

class MediaRetriever:

    def __init__(self) -> None:
        self.recent_media = []

    async def get_random_media(self) -> str:
        file = await self._get_random_media()

        if self.get_recent_media_max() <= 0:
            return file

        while file in self.recent_media:
            file = await self._get_random_media()
                
        self.recent_media.append(file)

        while len(self.recent_media) > self.get_recent_media_max():
            self.recent_media.pop(0)

        return file

    def get_recent_media_max(self) -> int:
        pass

    def has_media(self) -> bool:
        pass

    async def _get_random_media(self) -> str:
        pass
    
class MultiMediaRetriever(MediaRetriever):
    def __init__(self, media_retrieve_routines: list[MediaRetriever]):
        super().__init__()
        self.media_retrieve_routines = media_retrieve_routines

    def get_recent_media_max(self) -> int:
        return sum([mr.get_recent_media_max() for mr in self.media_retrieve_routines])
    
    def has_media(self) -> bool:
        return any([mr.has_media() for mr in self.media_retrieve_routines])

    async def _get_random_media(self):
        return await self.__get_media_retriever().get_random_media()

    def __get_media_retriever(self) -> MediaRetriever:
        retrievers_with_media = [mr for mr in self.media_retrieve_routines if mr.has_media()]
        return retrievers_with_media[random.randint(0, len(retrievers_with_media)-1)]
    
class ApiRoutineMediaRetrieve(MediaRetriever):
    def __init__(self, api_coroutine, recent_media_max=5):
        super().__init__()
        self.api_coroutine = asyncio.coroutine(api_coroutine)
        self.recent_media_max = recent_media_max

    def get_recent_media_max(self) -> int:
        return self.recent_media_max
    
    def has_media(self) -> bool:
        return True

    async def _get_random_media(self) -> str:
        return await self.api_coroutine()
    
class LocalFileMediaRetriever(MediaRetriever): 
    def __init__(self, media_folder, recent_media_max=5):
        super().__init__()
        self.media_folder = media_folder
        self.recent_media_max = recent_media_max

    def get_recent_media_max(self) -> int:
        file_count = max(self.__get_local_file_count(), 1)
        if file_count == 1:
            return 0
        
        return max(min(file_count / 2, self.recent_media_max), 0)

    async def _get_random_media(self) -> str:
        files = os.listdir(self.media_folder)
        return self.media_folder + files[random.randint(0, len(files)-1)]

    def has_media(self) -> bool:
        return self.__get_local_file_count() > 0
    
    def __get_local_file_count(self):
        if not os.path.exists(self.media_folder):
            return 0
        
        return len(os.listdir(self.media_folder))