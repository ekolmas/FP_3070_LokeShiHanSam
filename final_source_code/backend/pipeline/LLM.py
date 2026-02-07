import ast
import os
import requests
from dotenv import load_dotenv
import json

# load the api key
load_dotenv()
api_url = "https://openrouter.ai/api/v1/chat/completions"


def parse_llm_dialogue(llm_response):
    response = llm_response.strip()

    # Try to parse json first, because ' can break python string
    try:
        data = json.loads(response)
        if isinstance(data, list) and all(
            isinstance(sentence, str) for sentence in data
        ):
            return data
    except Exception as e:
        pass

    # If json doesnt work, use ast library to safely evaluate the string
    try:
        data = ast.literal_eval(response)
        if isinstance(data, list) and all(
            isinstance(sentence, str) for sentence in data
        ):
            return data
    except Exception as e:
        pass

    return None


def build_request_header(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Prototype Podcast Generator",
    }


def build_request_payload(model_endpoint, article):
    return {
        "model": model_endpoint,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a podcast script generator. Your task is to create a conversational podcast "
                    "between exactly two hosts who take turns speaking. The conversation must be based on "
                    "the provided news article. You must return ONLY a valid JSON array of strings. "
                    'Example: ["First turn", "Second turn"].'
                    "Do not use single quotes. Do not wrap in ``` code fences. No extra text."
                    "The conversation list must be chronological, alternate speakers naturally, and may include multiple "
                    "sentences per turn. Do not add commentary, explanations, or formatting outside the JSON."
                ),
            },
            {"role": "user", "content": article.get("content")},
        ],
        "max_tokens": 0,
    }


def generate_conversation_for_article(model_endpoint, article, openrouter_api_key):

    if openrouter_api_key is None:
        raise ValueError("Openrouter API key is missing")

    header = build_request_header(openrouter_api_key)
    payload = build_request_payload(model_endpoint, article)
    response = requests.post(api_url, headers=header, json=payload)
    if response.status_code != 200:
        raise RuntimeError(
            f"Something went wrong with the openrouter request, response: {response}"
        )
    else:
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        print(reply)
        parsed_reply = parse_llm_dialogue(reply)

        if parsed_reply == None:
            raise SyntaxError(
                f"Parse failed for article {article.get('title')} , reply: {reply}"
            )

        return parsed_reply
