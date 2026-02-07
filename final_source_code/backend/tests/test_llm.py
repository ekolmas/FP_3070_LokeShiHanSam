# Unit testing for large language model conversation generator
import os
import json
import types
import pytest
from pipeline.LLM import (
    parse_llm_dialogue,
    build_request_header,
    build_request_payload,
    generate_conversation_for_article,
)

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")


# first test: Ensure that the parsing function parses LLM response into a list
# successfully passed
def test_parse_llm_dialogue_returns_list():
    mock_llm_response = "['This is the first sentence','This is the second sentence','This is the third sentence']"
    result = parse_llm_dialogue(mock_llm_response)
    # Ensure that the result comes out in a list
    assert result == [
        "This is the first sentence",
        "This is the second sentence",
        "This is the third sentence",
    ]


# second test: Ensure that the parsing function handles invalid input
# successfully passed
def test_parse_llm_dialogue_handles_invalid_list():
    mock_llm_response = "This is not a list"
    result = parse_llm_dialogue(mock_llm_response)
    # Ensure that the result is an empty list for invalid input
    assert result is None


# third test: Ensure that the parsing function handles non-string elements in the list
# successfully passed
def test_parse_llm_dialogue_has_nonstring():
    mock_llm_response = "['This is valid', not valid, 'Another valid']"
    result = parse_llm_dialogue(mock_llm_response)
    # Ensure that the result is None when nonstring elements are present
    assert result is None


def test_build_request_header():
    mock_api_key = "This is a fake api key"
    result = build_request_header(mock_api_key)
    assert result == {
        "Authorization": f"Bearer {mock_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Prototype Podcast Generator",
    }


def test_build_request_payload():
    model_endpoint = "z-ai/glm-4.5-air:free"
    mock_article = {
        "content": "This article talks about how an automatic podcast generator is in the works by Loke Shi Han Sam"
    }
    result = build_request_payload(model_endpoint, mock_article)
    assert result == {
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
            {"role": "user", "content": mock_article.get("content")},
        ],
        "max_tokens": 0,
    }


def test_generate_conversation_for_article_handles_missing_api_key():
    model_endpoint = "z-ai/glm-4.5-air:free"
    article = {"content": "This is mock content"}

    with pytest.raises(ValueError):
        # Call the function with a missing API key for test
        generate_conversation_for_article(model_endpoint, article, None)


# Simulate bad request with a fake api key
def test_generate_conversation_fake_api_key():
    model_endpoint = "z-ai/glm-4.5-air:free"
    mock_api_key = "This is a fake api key"
    article = {
        "title": "Mock article",
        "content": "This is some content for a mock article",
    }

    with pytest.raises(RuntimeError):
        generate_conversation_for_article(model_endpoint, article, mock_api_key)


def test_gernerate_conversation_return_conversation_list():
    model_endpoint = "z-ai/glm-4.5-air:free"
    test_api_key = api_key
    article = {
        "title": "Tesla is beaten by BYD",
        "content": "The number one ev brand is now BYD and not tesla as of 2026 January. This comes after BYD and Tesla releases their 2025 Q4 numbers.",
    }

    result = generate_conversation_for_article(model_endpoint, article, test_api_key)
    print(result)
    assert isinstance(result, list) == True
