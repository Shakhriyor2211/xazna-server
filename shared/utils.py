import os
import uuid

import httpx
from django.core.files import File
from pydub import AudioSegment

from xazna import settings


async def send_post_request(payload, url, request_type="json"):
    async with httpx.AsyncClient(timeout=None) as client:
        if request_type == "json":
            response = await client.post(url, json=payload, timeout=None)
            return response

        else:
            files = {"file": (payload.name, payload, payload.content_type)}
            response = await client.post(url, files=files)
            return response


def generate_audio(bytes, fmt):
    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    temp_path = os.path.join(temp_dir, f"""audio.wav""")
    output_path = os.path.join(temp_dir, f"""audio.{fmt}""")

    os.makedirs(os.path.dirname(temp_dir), exist_ok=True)

    with open(temp_path, "wb") as f:
        f.write(bytes)

    try:
        if fmt == "wav":
            return File(open(temp_path, "rb"), name="audio.wav")

        audio = AudioSegment.from_file(temp_path, format="wav")
        audio.export(output_path, format=fmt)

        return File(open(output_path, "rb"), name=f"""audio.{fmt}""")



    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
