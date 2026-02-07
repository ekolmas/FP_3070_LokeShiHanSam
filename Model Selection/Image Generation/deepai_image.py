import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("DEEPAI_API_KEY")

prompt = "AI takes over the world, digital art, sci-fi, dramatic"

response = requests.post(
    "https://api.deepai.org/api/text2img",
    headers={"api-key": API_KEY},
    data={"text": prompt},
)

data = response.json()
print("Image URL:", data)
