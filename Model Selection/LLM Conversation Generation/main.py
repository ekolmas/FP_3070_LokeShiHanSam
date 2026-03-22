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
        "content": "Autonomous, AI-based players are coming to a gaming experience near you, and a new startup, Altera, is joining the fray to build this new guard of AI agents.The company announced Wednesday that it raised $9 million in an oversubscribed seed round, co-led by First Spark Ventures (Eric Schmidt’s deep-tech fund) and Patron (the seed-stage fund co-founded by Riot Games alums).The funding follows Altera’s previous raising a pre-seed $2 million from a16z SPEEDRUN and others in January of this year. Now, Altera wants to use the new capital to hire more scientists, engineers and team members to help with product development and growth.If the first wave of AI for end users was about AI bots; and more recently, AI “copilots” use generative AI to help understand and respond to increasingly sophisticated queries, then AI agents are emerging as the next stage of development. The focus is on how AI can be used to create increasingly more human-like, nuanced entities that can respond to and interact with actual humans.One early use case for these agents has been gaming — specifically to use in games that support modifications (mods) like Minecraft. Voyager is one recent project, built on the Minedojo framework, that creates and develops Minecraft AI agents, and this, too, is where Altera is getting its start.The company’s first product is an AI agent that can play Minecraft with you, “just like a friend” (the waitlist to try that out is here), but this seems to be just chapter one for the company. “We are building multi-agent worlds, opening up exciting opportunities in entertainment, market research, and more,” the company promises on its site. And after that? Robot dreams, it seems.“Creating the human qualities required to turn co-pilots into co-workers and exploring a world where digital humans are given a physical form factor,” Altera explains.At the helm of Altera is Robert Yang, a neuroscientist and former assistant professor at MIT. In December 2023, Yang and Altera’s other co-founders — Andrew Ahn, Nico Christie and Shuying Luo — stepped away from their applied research lab at MIT to focus on a new goal: developing AI agents (or “AI buddies,” as Yang calls them) with “social-emotional intelligence” that can interact with players and make their own decisions in-game.“It has been my life goal as a neuroscientist to go all the way and build a digital human being — redefining what we thought AI was capable of,” Yang told TechCrunch. That is not to say that Yang is coming from a misanthropic point of view. “Our solidly pro-human framework means that we are building agents that will enhance humanity, not replace it,” he insists.What is notable about Yang and Altera’s focus is its consumer focus. This stands in contrast with a big swing that we have seen in AI toward building models that can be used either to speed up or sometimes replace humans in enterprise environments. (Even with OpenAI, ChatGPT has certainly been a viral hit globally, but at its heart the startup has been trying to build a business around usage of its APIs.)“We see more potential in building agents within the gaming industry,” he said. “This approach allows us to iterate faster, collect data more effectively, and deliver a product where there are eager users and where emergent behavior is a feature, not a bug.”(And yes, in keeping with its consumer focus, you should not be surprised that, for now, the company is not talking about monetization at all.)Similar to the Voyager GPT-4-powered Minecraft bot, Altera’s autonomous agents are capable of playing Minecraft as if they were humans, performing tasks like building, crafting, farming, trading, mining, attacking, equipping items, chatting and moving around.Altera’s agents are designed to be companions for gamers, not assistants who do what you tell them to. Unlike NPCs (non-player characters), they have the freedom to make their own decisions, which could either make the game more entertaining or frustrating, depending on your playing style.In a video demo, Yang plays around with multiple scenarios, including one where he tries to convince the AI agent to attack other people. The bot is hesitant at first, typing in the chat, “I don’t want any trouble, can we just find a peaceful solution? Fighting won’t solve anything.” Yang taunts it, commanding others to attack the “weak” bot. It eventually defends itself and kills Yang’s Minecraft character. “I’ll make sure they regret crossing me,” the AI agent wrote.While the ending may be a little sinister, the gameplay feels no different from a regular session with friends, trolling and competing against each other.Altera is currently testing the model with 750 Minecraft players and plans to officially launch later in the summer. It’ll be available via Altera’s desktop app, which is free to download but will also come with paid features.Minecraft is just a starting point for Altera. The company eventually plans to bring the model to additional video games and other digital experiences. Altera’s AI agents “execute an action as code, meaning they can play any game without material customization,” Yang explained. For instance, it could work with Stardew Valley, he said. Altera will also integrate the technology with game engine SDKs for “broader developer use.”In addition to the recent investments by First Spark and Patron, Altera has gained support from a long list of high-profile investors, demonstrating confidence in the company’s potential. Altera boasts investors such as Alumni Ventures, a16z SPEEDRUN, Benchmark partner Mitch Lasky, Duolingo Chief Business Officer Bob Meese, Vamos Ventures, Valorant co-founder Stephen Lim and more.“There exists a massive opportunity to create AI companions that engage in all areas of our lives. However, today’s AI lacks critical traits like empathy, embodiment, and personal goals, which prevent it from forming real, lasting connections with people,” Aaron Sisto, partner at First Spark Ventures, said in a statement. “Robert and the team at Altera are leveraging deep expertise in computational neuroscience and LLMs to build radically new types of AI agents that are fun, unique, and persistent across platforms. We are thrilled to be a part of their journey.”",
    }
]

models = [
    "z-ai/glm-4.5-air:free",
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
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
