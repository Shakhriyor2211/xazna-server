import os
import httpx
from django.core.files import File
from pydub import AudioSegment
from xazna import settings
import soundfile as sf


async def send_post_request(payload, url, request_type="json"):
    async with httpx.AsyncClient(timeout=None) as client:
        if request_type == "json":
            response = await client.post(url, json=payload, timeout=None)
            return response

        else:
            files = {"file": (payload.name, payload, payload.content_type)}
            response = await client.post(url, files=files)
            return response


def generate_audio(chunks, fmt):
    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    temp_path = os.path.join(temp_dir, "audio.wav")
    output_path = os.path.join(temp_dir, f"audio.{fmt}")
    sf.write(temp_path, chunks, 24000, subtype="PCM_16")

    try:
        if fmt == "wav":
            return File(open(temp_path, "rb"), name="audio.wav")

        audio = AudioSegment.from_file(temp_path, format="wav")
        audio.export(output_path, format=fmt)

        return File(open(output_path, "rb"), name=f"""audio.{fmt}""")

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)
        os.remove(temp_path)


def get_audio_duration(file):
    audio = AudioSegment.from_file(file)
    return len(audio) / 1000