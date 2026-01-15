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
    },
    {
        "source": {"id": "null", "name": "GlobeNewswire"},
        "author": "AstuteAnalytica India Pvt. Ltd.",
        "title": "Permanent Magnet Market Forecast 2025-2033: Total Revenues to Reach $67.25 Billion – Astute Analytica",
        "description": "The market’s growth is being propelled by a confluence of transformative industrial trends, led by the electric vehicle (EV) sector, which accounted for 22.9 million EV motor units produced in 2024, with demand forecast to rise to 28.1 million units in 2025. …",
        "url": "https://www.globenewswire.com/news-release/2026/01/14/3218958/0/en/Permanent-Magnet-Market-Forecast-2025-2033-Total-Revenues-to-Reach-67-25-Billion-Astute-Analytica.html",
        "urlToImage": "https://ml.globenewswire.com/Resource/Download/a77988df-ad1a-4619-9a4e-367c858dc70e",
        "publishedAt": "2026-01-14T16:14:00Z",
        "content": "Chicago, Jan. 14, 2026 (GLOBE NEWSWIRE) -- The global permanent magnet market was valued at 32.86 billion in 2024 and is expected to reach US$ 67.25 billion by 2033, growing at a CAGR of 8.47% from 2025 to 2033.The permanent magnet market is experiencing a transformative surge propelled by profound industrial revolutions, with the automotive sector emerging as the foremost force reshaping demand. In 2024 alone, electric vehicle motor production soared to an impressive 22.9 million units, with forecasts projecting a strong climb to 28.1 million units by 2025.Request Sample Pages: https://www.astuteanalytica.com/request-sample/permanent-magnet-marketA dominant share of this growth 19.7 million units in 2024, came from Permanent Magnet Synchronous Motors, highlighting their critical role. This rapid expansion translated to a substantial consumption of 37 kilotons of rare earth elements in 2024, with expectations to escalate to 43 kilotons in 2025. Industry frontrunners like Tesla and BYD, which surpassed production milestones of 2.1 million and 3 million electric vehicles, respectively, in 2024, exemplify this accelerating trend.Demand is diversifying beyond automobiles in the permanent magnet market. The renewable energy sector is a major consumer. China's new wind power installations alone totaled 80.45 gigawatts in 2024, requiring 9,735 metric tons of NdFeB magnets. Industrial automation further fuels growth, with China's industrial robot production estimated to reach 941,000 units in 2025. Even established sectors contribute heavily; air conditioner production hit 270 million units in 2024, creating a demand for 21,000 metric tons of NdFeB magnets.Power-Hungry Hyperscale Data Centers Drive Specialized Magnet IntegrationThe explosive growth of data infrastructure is creating a significant, non-obvious demand channel for the Permanent magnet market. In 2024 alone, construction began on more than 300 new hyperscale data centers globally. Each of these facilities requires thousands of high-efficiency motors for cooling. More than 1.5 million high-efficiency permanent magnet motors were installed in data center HVAC systems in 2024. The total power consumption for these new facilities is estimated to exceed 15 gigawatts by 2025. This intense energy usage is propelling innovation in cooling technology.The adoption of direct-to-chip liquid cooling is a key trend, with an estimated 450,000 specialized magnetic-drive pumps deployed in these systems in 2024. Projections for 2025 show this number exceeding 700,000 units. These pumps deliver superior reliability and control. Furthermore, more than 25,000 magnetic levitation chillers were installed in data centers in 2024 for frictionless, efficient operation. The industry saw an investment of more than US$ 2 billion in 2024 specifically for upgrading legacy cooling systems to magnet-based solutions. In 2025, an estimated 50 petabytes of data will be generated every second, further driving the construction of these power-hungry facilities.Urban Air Mobility Creates a High-Value Frontier for Permanent MagnetsA new high-value frontier is opening in the Permanent magnet market, pushed by aerospace modernization and the dawn of urban air mobility. In 2024, the development pipeline for electric vertical takeoff and landing (eVTOL) aircraft included more than 400 distinct prototypes globally. Major players in this space collectively placed pre-orders for more than 15,000 eVTOL aircraft by the end of 2024. Each aircraft needs between 8 to 16 lightweight, power-dense permanent magnet motors for propulsion. This translates to a near-term demand for more than 120,000 high-performance motors.Investment in the urban air mobility sector surpassed US$ 7 billion in 2024. The 'more-electric aircraft' (MEA) initiative in commercial aviation is also a key driver for the permanent magnet market. In 2024, Airbus and Boeing logged orders for more than 2,000 MEA-compliant aircraft, which replace heavy hydraulic systems with lighter electromechanical actuators using powerful magnets. More than 500,000 high-performance magnetic actuators were ordered for these new aircraft builds in 2024. Also, the booming satellite industry, which launched more than 2,500 new satellites in 2024, utilizes permanent magnets in reaction wheels and actuators for positioning. This demand is forecast to grow as an extra 12,000 satellites are planned for launch by the end of 2025.Superior Pull and Miniaturization Capabilities Cement NdFeB Market LeadershipNeodymium Iron Boron (NdFeB) magnets are the undisputed leaders in the permanent magnet market, commanding an impressive 48.02% market share. Their dominance stems from an exceptional energy product, which can exceed 55 MGOe, allowing for significant device miniaturization. For instance, their use in smartphone voice coil motors, measuring just a few millimeters, is critical for audio performance. A key driver is the electric vehicle (EV) sector, where a single EV traction motor often utilizes between 1.5 kg and 2.5 kg of NdFeB magnets. With global EV production estimated to surpass 20 million units annually by 2025, the demand is set to soar. In the renewable energy sector, a Vestas V164-10.0 MW offshore wind turbine requires approximately 2,000 kg of these powerful magnets, showcasing their role in large-scale energy generation.The pull force of a small N52 grade NdFeB magnet, just 1 inch in diameter, can exceed 150 lbs, a testament to its power. This strength is vital in industrial robotics, where servo motors require high torque in compact designs, with some motors containing over 50 individual magnet pieces. Global production capacity across the permanent magnet market is expanding rapidly, with major manufacturers planning to add more than 30,000 tons of new capacity by the end of 2025 to meet escalating demand. The price of neodymium oxide, a key raw material, has seen fluctuations between US$ 90/kg and US$ 120/kg in 2024, directly impacting production costs.Europe Accelerates Domestic Production to Secure Magnet Supply for EVs and RenewablesEurope is aggressively working to establish a regional and resilient Permanent magnet market, driven by strategic initiatives like the Critical Raw Materials Act. A landmark development is Solvay’s inauguration of a new rare earth processing line in La Rochelle, France, in April 2025, creating the largest separation facility outside China. The facility currently produces 4,000 metric tons of separated oxides annually and will start producing magnet-grade materials in 2025. By 2030, Solvay aims to satisfy 30% of European demand for these materials. These efforts are crucial as the continent's demand continues to rise, fueled by its automotive and renewable energy sectors.The end-market demand is robust across the permanent magnet market. In the UK, the September 2024 renewables auction awarded contracts for approximately 5.3 GW of new offshore wind capacity, a significant consumer of large permanent magnets. These projects are part of a larger award of 9.6 GW across 131 new green infrastructure projects. Germany, a primary importer of Chinese magnets, is also a major automotive producer, providing a substantial demand base. The focus is now on connecting these demand centers with nascent European production abilities, fostering a more secure and autonomous supply chain.Permanent Magnet Market Major Players:TDK CorporationShin-Etsu Chemical Co., Ltd.Daido Steel Co., Ltd .MP Materials Corp.Lynas Rare Earths Ltd.Ningbo Yunsheng Co., Ltd.Beijing Zhong Ke San Huan Hi-Tech Co., Ltd.VACUUMSCHMELZE GmbH & Co. KG (VAC)Arnold Magnetic TechnologiesElectron Energy CorporationAdams Magnetic Products Co.Hitachi Metals, Ltd.Other Prominent PlayersKey Market Segmentation:By Magnet TypeNeodymium Iron Boron (NdFeB) MagnetsSamarium Cobalt (SmCo) MagnetsAlnico MagnetsFerrite MagnetsBy GradeLow GradeMid-GradeHigh GradeBy Manufacturing ProcessSintered MagnetsBonded MagnetsInjection MagnetsHot Pressed MagnetsBy End UserAutomotiveConsumer ElectronicsIndustrial EquipmentAerospace & DefenseSemiconductorMilitaryOthersBy Distribution ChannelOnlineOfflineDirect SalesDistributorsBy RegionNorth AmericaEuropeAsia PacificMiddle East and AfricaSouth AmericaFor more information about this report visit: https://www.astuteanalytica.com/industry-report/permanent-magnet-marketAbout Astute AnalyticaAstute Analytica is a global market research and advisory firm providing data-driven insights across industries such as technology, healthcare, chemicals, semiconductors, FMCG, and more. We publish multiple reports daily, equipping businesses with the intelligence they need to navigate market trends, emerging opportunities, competitive landscapes, and technological advancements.With a team of experienced business analysts, economists, and industry experts, we deliver accurate, in-depth, and actionable research tailored to meet the strategic needs of our clients. At Astute Analytica, our clients come first, and we are committed to delivering cost-effective, high-value research solutions that drive success in an evolving marketplace.",
    },
    {
        "source": {"id": "", "name": "CNBC"},
        "author": "",
        "title": "Musk says Tesla is moving Full Self-Driving to a monthly subscription",
        "description": "Tesla is lagging Waymo in autonomous mobility as the Alphabet-owned driverless car service topped 450,000 paid weekly rides in December.",
        "url": "https://www.cnbc.com/2026/01/14/musk-tesla-full-self-driving-subscription-fsd.html",
        "urlToImage": "https://image.cnbcfm.com/api/v1/image/108168278-17518962972025-06-13t010710z_885255829_rc2gk1a9xltd_rtrmadp_0_space-warfare.jpeg?v=1753301789&w=1920&h=1080",
        "publishedAt": "2026-01-14T16:12:33Z",
        "content": "TeslaCEO Elon Musk said Wednesday that the electric vehicle maker will stop selling its Full Self-Driving (Supervised) software for a flat rate and instead make it only available as a monthly subscription.“Tesla will stop selling FSD after Feb 14,” Musk said in an early morning post on his social media platform X. “FSD will only be available as a monthly subscription thereafter.”Shares of the company fell more than 2% Wednesday.FSD, which starts at $99 per month, is key to the future of the company as Musk tries to establish Tesla as a leader in autonomous mobility.Tesla did not immediately respond to a request for comment.Tesla launched a robotaxi service with limited availability in Austin, Texas, last year, and the company also offers ride-hailing in San Francisco, though with a driver behind the wheel at all times. The company is way behind Alphabet’sWaymo in driverless service. In December, Waymo reached more than 450,000 weekly paid rides, according to an investor letter from Tiger Global seen by CNBC.Waymo operates in Austin, the San Francisco area, Phoenix, Atlanta and Los Angeles and is targeting expansion to several more cities in 2026.Tesla reported fourth-quarter delivery and production numbers at the beginning of January, wrapping the second-straight annual drop for the EV maker. Fourth-quarter deliveries of 418,227 were about 16% lower than a year ago, and production numbers were down 5.5% from a year earlier.Tesla reports fourth-quarter earnings on Jan. 28.",
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
