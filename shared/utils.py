import re
from io import BytesIO
import secrets
from datetime import timedelta
from django.utils import timezone
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



def generate_email_otp(old_code):
    new_code = "".join(secrets.choice("0123456789") for _ in range(6))
    while old_code == new_code:
        new_code = "".join(secrets.choice("0123456789") for _ in range(6))
    return new_code, timezone.now() + timedelta(minutes=settings.EMAIL_EXPIRE_TIME)


def generate_title(message):
    title = ""

    words = re.split(r"\s+|(?=[.,;?!])|(?<=[.,;])", message)

    for i, word in enumerate(words):
        if i > 0 and len(word) + len(title) > 20:
            break

        if i > 0 and not word in [".", ",", ";", "?", "!"]:
            title += " "

        title += word

    return title


def convert_to_wav(audio_file):
    audio_file.seek(0)
    audio_bytes = audio_file.read()

    audio_io = BytesIO(audio_bytes)

    original_format = audio_file.name.split('.')[-1].lower()

    audio = AudioSegment.from_file(audio_io, format=original_format)

    wav_io = BytesIO()
    audio.set_frame_rate(44100).set_channels(1).set_sample_width(2).export(
        wav_io, format="wav"
    )

    wav_io.seek(0)

    return wav_io