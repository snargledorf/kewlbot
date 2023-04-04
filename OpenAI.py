import os

import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

async def generate_image(prompt: str) -> str:
    response = await openai.Image.acreate(prompt=prompt, n=1, size="256x256")
    return response["data"][0]["url"]