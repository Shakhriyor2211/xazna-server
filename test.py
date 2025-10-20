from openai import OpenAI
from datetime import datetime
import time

openai_api_key = "EMPTY"
openai_api_base = "https://testtts.xb.uz/llm/v1"
client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)

def timeformatter2(t):
    return datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

def message_streaming(conversation):
    # yield "Hozircha test uchunda bu endi"
    model = client.models.list().data[0].id
    print("LLM stream begin:", timeformatter2(int(time.time())))
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=conversation,
            stream=True,
            temperature=0.7,
            max_tokens=200,
        )
        buffer = ""
        for chunk in stream:
            delta = chunk.choices[0].delta
            token = delta.content if delta else ""
            buffer += token
            if any(buffer.endswith(d) for d in [".", "!", "?"]):
                yield buffer.strip()
                buffer = ""
        if buffer.strip():
            yield buffer.strip()
    except Exception as e:
        print("[LLM ERROR]", e)
    print("LLM stream end.")



conversation = [
    {"role": "user", "content": "Senga o'zbek tilida murojaat qilishadi. Sen faqat o'zbek tilida gaplashishing kerak."},
    {"role": "assistant", "content": "Albatta! Faqat o'zbek tilida javob qaytaraman."},
]

for reply_chunk in message_streaming(conversation):
    print(reply_chunk)