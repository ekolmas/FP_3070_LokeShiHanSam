# This is the main script that calls other modules to generate the podcast

import sys
import json
from LLM import generate_podcast_script
from TTS import generate_podcast_audio

#Same article content as in LLM.py 
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

def main():
    dummy_news_article = content_json

    #generate dialogue using LLM.py
    dialogue = generate_podcast_script(dummy_news_article)
    podcast_audio_path  = generate_podcast_audio(dialogue, output_directory='tts_out')

    results = {
        "response_code": 200,
        "title": dummy_news_article['title'],
        "dialogue": dialogue,
        "podcast_audio_path": podcast_audio_path
    }

    print(json.dumps(results))

if __name__ == "__main__":
    main()