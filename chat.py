import os
from openai import OpenAI

API_KEY = "sk-LqCf11ej9dj70ObUG956eQ"
BASE_URL = "https://llm.t1v.scibox.tech/v1"

try:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    resp = client.chat.completions.create(
        model="Qwen2.5-72B-Instruct-AWQ",
        messages=[
            {"role": "system", "content": "Ты — полезный ассистент для команды на хакатоне."}, # промпт для системы 
            {"role": "user", "content": "Предложи одну креативную идею для IT-проекта."}, # вопрос для модели
        ],
        temperature=0.8, # насколько разрешить модели мыслить нестандартно? Значение от 0 до 2, сейчас мыслит больше шаблонно, чем стандартно
        max_tokens=400, # сколько символов выведется при ответе? на данный момент 400
    )

    print(resp.choices[0].message.content)

except Exception as e:
    print("\n--- ПРОИЗОШЛА ОШИБКА ---")
    print(e)