import ast
import os
import requests
from dotenv import load_dotenv
import json

# load the api key
load_dotenv()
api_url = "https://openrouter.ai/api/v1/chat/completions"


# Function purpose: parse the conversation list produced by the open router llm conversation generator
def parse_llm_dialogue(llm_response):
    response = llm_response.strip()

    # try to parse as json first
    try:
        data = json.loads(response)
        # Check if format of the conversation list is correct
        # Correct format ["string","All string"]
        if isinstance(data, list) and all(
            isinstance(sentence, str) for sentence in data
        ):
            return data
    # Catch exception
    except Exception as e:
        pass

    # if json doesnt work, try to parse using ast library
    try:
        data = ast.literal_eval(response)
        # Check if format of the conversation list is correct
        # Correct format ["string","All string"]
        if isinstance(data, list) and all(
            isinstance(sentence, str) for sentence in data
        ):
            return data
    except Exception as e:
        pass

    # If nothing works due to parsing error, return None
    return None


# Function purpose: build request header for OpenRouter request
def build_request_header(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Prototype Podcast Generator",
    }


# Function purpose: build request payload for OpenRouter request with system prompt
def build_request_payload(model_endpoint, article):
    article_contents = (
        (article.get("title") or "")
        + (article.get("description") or "")
        + (article.get("content") or "")
    )
    return {
        "model": model_endpoint,
        "messages": [
            {
                "role": "user",
                "content": (
                    "You are a podcast script generator. Your task is to create a conversational podcast "
                    # 2 host conversation that is factual
                    "between exactly two hosts who take turns speaking. The conversation must be based on the provided news article."
                    # Ensure that the format is a  JSON array of strings
                    " You must return ONLY a valid JSON array of strings. "
                    # give example of the format
                    'Example: ["First turn", "Second turn"].'
                    # Ensure that the response doesnt using single quote, code fences and extra texts
                    "Do not use single quotes. Do not wrap in ``` code fences. No extra text."
                    # Make sure that the conversation list is is natural and alternating
                    "The conversation list must be chronological, alternate speakers naturally, and may include multiple "
                    # Avoid commentary and explanations
                    "sentences per turn. Do not add commentary, explanations, or formatting outside the JSON."
                    + article_contents
                ),
            }
        ],
    }


# Function purpose: Call OpenRouter API to generate conversation for the one article
def generate_conversation_for_article(model_endpoint, article, openrouter_api_key):
    # Check if the ENV contains open router key
    if openrouter_api_key is None:
        raise ValueError("Openrouter API key is missing")

    # Build header using function
    header = build_request_header(openrouter_api_key)
    # Build payload using function
    payload = build_request_payload(model_endpoint, article)
    # Send openrouter API request
    response = requests.post(api_url, headers=header, json=payload)
    # Check if response is successful
    if response.status_code != 200:
        # If not successful raise error with response for debugging
        raise RuntimeError(f"OpenRouter error {response.status_code}: {response.text}")
    else:
        # If successful parse the response and extract the conversation reply
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        parsed_reply = parse_llm_dialogue(reply)

        # If parsing fails raise error with the LLM reply for debugging
        if parsed_reply == None:
            raise SyntaxError(
                f"Parse failed for article {article.get('title')} , reply: {reply}"
            )

        return parsed_reply
