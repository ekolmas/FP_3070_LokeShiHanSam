import os
import requests
from dotenv import load_dotenv

#Load environment variables from .env
load_dotenv()

#Get API key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

#If cannot find API key
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Prototype Podcast Generator",
}

payload = {
    "model": "amazon/nova-2-lite-v1:free",
    "messages": [
        {
            "role": "system",
            "content": "You are a podcast script generator. Your task is to create a conversational podcast between exactly two hosts who take turns speaking (for example: Sam and Elle). The conversation must be based ONLY on the provided news article. You must return your answer strictly in valid JSON and nothing else. The JSON must follow this exact structure: { \"conversation\": [\"string\", \"string\"], \"news_title\": \"string\", \"news_source\": \"string\" }. The conversation array must be chronological, alternate speakers naturally, and may include multiple sentences per turn. Do not add commentary, explanations, or formatting outside the JSON."
        },
        {
            "role": "user",
            "content": "Generate a two-host podcast conversation based on the following news article. Use the article title and source name exactly as provided. Here is the article data:\n\n{\n  \"source\": {\n    \"id\": null,\n    \"name\": \"Motley Fool\"\n  },\n  \"author\": \"Danny Vena, CPA, Danny Vena, CPA\",\n  \"title\": \"Broadcom CEO Hock Tan Just Delivered Incredible News for Nvidia Stock Investors - The Motley Fool\",\n  \"description\": \"The data center and semiconductor specialist just provided the clearest evidence yet that the adoption of artificial intelligence (AI) continues to gain steam.\",\n  \"url\": \"https://www.fool.com/investing/2025/12/12/broadcom-ceo-hock-tan-just-delivered-incredible-ne/\",\n  \"urlToImage\": \"https://g.foolcdn.com/image/?url=https%3A%2F%2Fg.foolcdn.com%2Feditorial%2Fimages%2F846857%2Fnvidias-santa-clara-headquarters.jpg&w=1200&op=resize\",\n  \"publishedAt\": \"2025-12-12T17:35:00Z\",\n  \"content\": \"The data center and semiconductor specialist just provided the clearest evidence yet that the adoption of artificial intelligence (AI) continues to gain steam...\"\n}"
        }
    ],
    "max_tokens": 0
}

response = requests.post(API_URL, headers=headers, json=payload)

if response.status_code != 200:
    print("Request failed:")
    print(response.status_code, response.text)
else:
    data = response.json()
    print("raw response data:")
    print(data)
    print("=====================")
    reply = data["choices"][0]["message"]["content"]
    print("LLM response:")
    print(reply)
