# backend/tests/test_pipeline_one_article.py
import os
from pathlib import Path
import importlib
import pytest
from dotenv import load_dotenv
from pipeline.main import run_pipeline

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path, override=False)


# Test purpose: to build a newsapi like article for testing
def _one_dummy_article():
    return {
        "source": {"id": "unit-test", "name": "Unit Test News"},
        "author": "Tester",
        "title": "Test Article: AI podcast pipeline should handle one article",
        "description": "This is a short description used for testing.",
        "url": "https://example.com/test-article-1",
        "urlToImage": "https://example.com/test.jpg",
        "publishedAt": "2026-02-06T00:00:00Z",
        "content": "This is a test content body for TF-IDF and prompt context.",
    }


# Test purpose: to build a user preference profile that matches the dummy article
def _basic_user_pref():
    return {
        "preferences": {
            "sources": ["unit-test"],
            "topics": ["technology"],
            "style": ["daily"],
        }
    }


# Test purpose: ensure that full pipeline can process article and generate an audio podcast
def test_pipeline_one_article_integration_real():
    payload = {
        "articles": [_one_dummy_article()],
        "user_pref": _basic_user_pref(),
        "model_endpoint": os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.5-air:free"),
    }

    output = run_pipeline(payload)

    assert output["ok"] is True
    assert len(output["recommended"]) == 1
    audio_path = Path(output["recommended"][0]["audio_path"])
    assert audio_path.exists()
