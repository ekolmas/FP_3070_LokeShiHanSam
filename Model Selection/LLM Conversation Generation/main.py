# Author: Loke Shi Han, Sam
# The purpose of this file is to generate 3  conversations each from 3 news article from each of the 3 models selected for evaluation
# All LLM models are accessed through Openrouter API
import os
import requests
from dotenv import load_dotenv
import ast

# get the openrouter api key from .env file
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Prototype Podcast Generator",
}

newsArticles = [
    {
        "source": {"id": "techcrunch", "name": "TechCrunch"},
        "author": "Lauren Forristal",
        "title": "Bye-bye bots: Altera's game-playing AI agents get backing from Eric Schmidt | TechCrunch",
        "description": "Autonomous, AI-based players are coming to a gaming experience near you, and a new startup, Altera, is joining the fray to build this new guard of AI Research company Altera raised $9 million to build AI agents that can play video games alongside other player…",
        "url": "https://techcrunch.com/2024/05/08/bye-bye-bots-alteras-game-playing-ai-agents-get-backing-from-eric-schmidt/",
        "urlToImage": "https://techcrunch.com/wp-content/uploads/2024/05/Minecraft-keyart.jpg?resize=1200,720",
        "publishedAt": "2024-05-08T15:14:57Z",
        "content": "Autonomous, AI-based players are coming to a gaming experience near you, and a new startup, Altera, is joining the fray to build this new guard of AI agents.\r\nThe company announced Wednesday that it … [+6416 chars]",
    },
    {
        "source": {"id": "", "name": "Elearningindustry.com"},
        "author": "Christopher Pappas",
        "title": "Biggest AI Companies In 2026: Leaders Shaping The Future Of Artificial Intelligence",
        "description": 'AI is no longer an experiment, waiting to show real-world results and impact. It\'s entering a new phase. It has shown its capabilities when we humans know how to use it properly. So, 2026 will be the year more and more companies will adopt "smart" solutions a…',
        "url": "https://elearningindustry.com/biggest-ai-companies-leaders-shaping-the-future-of-artificial-intelligence",
        "urlToImage": "https://cdn.elearningindustry.com/wp-content/uploads/2026/01/Biggest-AI-Companies-in-2026_Leaders-Shaping-the-Future-of-Artificial-Intelligence.png",
        "publishedAt": "2026-01-12T14:00:41Z",
        "content": "The AI Landscape In 2026\r\nHave you ever wondered how many AI companies are operating? 212,230 companies, of which 62,184 are startups. Not only that, but approximately 2049 new companies are founded … [+23853 chars]",
    },
    {
        "source": {"id": "business-insider", "name": "Business Insider"},
        "author": "Tom Carter",
        "title": "Tesla hit with another lawsuit over 'defective' door handles",
        "description": "The class-action lawsuit is the latest in a long line of complaints over Tesla's electronically powered door handles.",
        "url": "https://www.businessinsider.com/tesla-lawsuit-defective-door-handles-model-s-2026-1",
        "urlToImage": "https://i.insider.com/6964eb0f64858d02d21827c1?width=1200&format=jpeg",
        "publishedAt": "2026-01-12T13:31:43Z",
        "content": "The new lawsuit is on behalf of owners of 2014-2016 Tesla Model S vehicles.Sjoerd van der Wal/Getty Images\r\n<ul><li>Tesla has been hit by another lawsuit over its futuristic flush door handles.</li><… [+3461 chars]",
    },
]

models = [
    "z-ai/glm-4.5-air:free",
    # "openai/gpt-oss-120b:free",
    # "nvidia/nemotron-3-nano-30b-a3b:free",
]
results = [[None for article in newsArticles] for model in models]


# For each model generate a conversation for each article
def generateConversations():
    for i, model in enumerate(models):
        for j, article in enumerate(newsArticles):
            openrouter_payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a podcast script generator. Your task is to create a conversational podcast between exactly two hosts who take turns speaking. The conversation must be based on the provided news article. You must return your answer strictly in a list and nothing else. The list must follow this exact structure: ['This is the first sentence','this is the second sentence']. The conversation list must be chronological, alternate speakers naturally, and may include multiple sentences per turn. Do not add commentary, explanations, or formatting outside the JSON.",
                    },
                    {"role": "user", "content": article.get("content")},
                ],
                # set max token to 0 to ensure no limit on response length
                "max_tokens": 0,
            }

            response = requests.post(API_URL, headers=headers, json=openrouter_payload)
            if response.status_code != 200:
                print("Request failed")
                print(response.status_code, response.text)
                return
            else:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
                parsed = parse_llm_dialogue(reply)

                if parsed is None:
                    print(
                        f"Parse failed for model={model}, article={article.get('title')}"
                    )
                    results[i][j] = []
                else:
                    results[i][j] = parsed

    for modelIndex, modelResults in enumerate(results):
        print(models[modelIndex], " results: ", modelResults)
        print("=====================")


# Function to parse the LLM response into a dialogue list
def parse_llm_dialogue(reply):
    reply = reply.strip()

    # try to parse using ast.literal_eval
    try:
        data = ast.literal_eval(reply)
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            return data
    except Exception as e:
        return


# Main function
if __name__ == "__main__":
    generateConversations()
