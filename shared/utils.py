from io import BytesIO

import httpx
from django.core.files import File
from pydub import AudioSegment


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
    audio_segment = AudioSegment(chunks.tobytes(), frame_rate=24000, sample_width=2, channels=1)
    buffer = BytesIO()
    audio_segment.export(buffer, format=fmt)
    buffer.seek(0)
    return File(buffer, name=f"""audio.{fmt}""")


def get_audio_duration(file):
    audio = AudioSegment.from_file(file)
    return len(audio) / 1000


def text_decode(match):
    letters = {
        "Ğ": "G'",
        "ğ": "g'",
        "Õ": "O'",
        "õ": "o'",
        "Ş": "Sh",
        "ş": "sh",
        "Ç": "Ch",
        "ç": "ch"
    }

    return letters[match.group()]
