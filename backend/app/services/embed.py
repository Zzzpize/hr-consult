import json
import numpy as np
from openai import OpenAI

API_KEY = "sk-LqCf11ej9dj70ObUG956eQ"
BASE_URL = "https://llm.t1v.scibox.tech/v1"
client = OpenAI(api_key = API_KEY, base_url = BASE_URL)

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model = "bge-m3",
        input = text
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

with open("backend/app/services/career_plans.json", "r") as f: career_plans = json.load(f)

with open("backend/app/services/user_profile.json", "r") as f: user_profile = json.load(f)

user_text = " ".join(user_profile["skills"])
user_vec = get_embedding(user_text)

best_match, best_score = None, -1
for plan in career_plans:
    plan_text = f"{plan['target_role']} {plan['description']}"
    plan_vec = get_embedding(plan_text)
    score = cosine_similarity(user_vec, plan_vec)
    if score > best_score:
        best_match, best_score = plan, score

print("Лучший план:", best_match["target_role"])
print("Score:", best_score)