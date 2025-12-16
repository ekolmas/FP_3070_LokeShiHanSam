import os
import requests
from dotenv import load_dotenv
import ast

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

content_json = {
"source": {
"id": "techcrunch",
"name": "TechCrunch"
},
"author": "Lauren Forristal",
"title": "Bye-bye bots: Altera's game-playing AI agents get backing from Eric Schmidt | TechCrunch",
"description": "Autonomous, AI-based players are coming to a gaming experience near you, and a new startup, Altera, is joining the fray to build this new guard of AI Research company Altera raised $9 million to build AI agents that can play video games alongside other player…",
"url": "https://techcrunch.com/2024/05/08/bye-bye-bots-alteras-game-playing-ai-agents-get-backing-from-eric-schmidt/",
"urlToImage": "https://techcrunch.com/wp-content/uploads/2024/05/Minecraft-keyart.jpg?resize=1200,720",
"publishedAt": "2024-05-08T15:14:57Z",
"content": "Autonomous, AI-based players are coming to a gaming experience near you, and a new startup, Altera, is joining the fray to build this new guard of AI agents.\r\nThe company announced Wednesday that it … [+6416 chars]"
}

# Function to parse the LLM response into a dialogue list 
def parse_llm_dialogue(reply):
    reply = reply.strip()

    #try to parse using ast.literal_eval
    try:
        data = ast.literal_eval(reply)
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            return data
    except Exception as e:
        #print("Error when parsing LLM response:", e)
        return

def generate_podcast_script(article_content):

    openrouter_payload = {
        "model": "amazon/nova-2-lite-v1:free",
        "messages": [
            {
                "role": "system",
                "content": "You are a podcast script generator. Your task is to create a conversational podcast between exactly two hosts who take turns speaking. The conversation must be based on the provided news article. You must return your answer strictly in a list and nothing else. The list must follow this exact structure: ['This is the first sentence','this is the second sentence']. The conversation list must be chronological, alternate speakers naturally, and may include multiple sentences per turn. Do not add commentary, explanations, or formatting outside the JSON."
            },
            {
                "role": "user",
                "content": str(content_json)
            }
        ],
        # set max token to 0 to ensure no limit on response length
        "max_tokens": 0
}

    response = requests.post(API_URL, headers=headers, json=openrouter_payload)

    if response.status_code != 200:
        #print("Request failed:")
        #print(response.status_code, response.text)
        return
    else:
        data = response.json()
        #print("=====================")
        reply = data["choices"][0]["message"]["content"]
        #print("LLM response:")
        #print(reply)
        return parse_llm_dialogue(reply)
    
#if __name__ == "__main__":
#    generate_podcast_script(content_json)