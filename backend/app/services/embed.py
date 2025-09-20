from openai import OpenAI

API_KEY = "sk-LqCf11ej9dj70ObUG956eQ"
BASE_URL = "https://llm.t1v.scibox.tech/v1"

texts_to_embed = [
    "Хакатон — это марафон для программистов.",
    "Команда пишет код всю ночь.",
    "Солнечная погода на пляже."
]

try:
    client = OpenAI(api_key = API_KEY, base_url = BASE_URL)
    print(f"Отправляю {len(texts_to_embed)} текстов на векторизацию моделью 'bge-m3'...")
    emb_response = client.embeddings.create(
        model = "bge-m3",
        input = texts_to_embed
    )
    num_embeddings = len(emb_response.data)
    print(f"Получено эмбеддингов: {num_embeddings}")
    if num_embeddings > 0:
        vector_dimension = len(emb_response.data[0].embedding)
        print(f"Размерность каждого вектора (эмбеддинга): {vector_dimension}")
        print(f"Пример части первого вектора: {emb_response.data[0].embedding[:5]}")
    if num_embeddings == len(texts_to_embed):
        print("Тест эмбеддинг-модели прошел успешно!")
    else:
        print("Тест прошел, но количество эмбеддингов не совпадает с количеством текстов!")

except Exception as e:
    print(f"\n--- ПРОИЗОШЛА ОШИБКА ---{e}")