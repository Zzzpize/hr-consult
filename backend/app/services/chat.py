import os
from openai import OpenAI

API_KEY = "sk-LqCf11ej9dj70ObUG956eQ"
BASE_URL = "https://llm.t1v.scibox.tech/v1"

def exchange(system_prompt: str, user_text: str, temperature: float = 0.8, max_tokens: int = 400):
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        resp = client.chat.completions.create(
            model = "Qwen2.5-72B-Instruct-AWQ",
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature = temperature,
            max_tokens = max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"\n--- ПРОИЗОШЛА ОШИБКА ---\n{e}"
    
def question(target, disclaimer):
    answer = exchange(f"Попробуй вычленить из ответа пользователя {target} и запиши через пробел. Если не получится – верни строчку 'system message: name is not found'\n" + disclaimer, input())
    while answer.lower() == "system message: name is not found":
        print(exchange(f"Переспроси пользователя его {target}, так как ты не смог его вычленить из ответа\n" + disclaimer, ""))
        answer = exchange(f"Попробуй вычленить из ответа пользователя {target} и запиши его через пробел. Если не получится – верни строчку 'system message: name is not found'\n" + disclaimer, input())
    return answer

def conversation():
    with open("backend/app/services/disclaimer.txt", "a+", encoding = "utf-8") as f:
        f.write("Обращения на 'Вы' всегда пиши с большой буквы. Будь вежливым, но не жеманным и льстительным.")
        disclaimer = (f.seek(0) or f.read())
        print(exchange("Как-нибудь перефразируй фразу, оставив смысл прежним\n" + disclaimer, "Привет! Я умный HR-консультант, который поможет Вам подняться по карьерной лестнице в компании. Для начала работы, пожалуйста, напишите свое ФИО."))
        name = question("ФИО", disclaimer)
        f.write(f"\nИмя пользователя – {name}. При необходимости обращайся к нему по имени.")
        disclaimer = (f.seek(0) or f.read())
        print(exchange("Спроси пользователя, в каком отделе он работает и какую должность занимает\n" + disclaimer, ""))
        place = question("отдел и должность", disclaimer)
        f.write(f"\nОтдел и должность – {place.lower()}.\n")
        disclaimer = (f.seek(0) or f.read())
    os.remove("backend/app/services/disclaimer.txt")

def main():
    conversation()

if __name__ == "__main__":
    main()