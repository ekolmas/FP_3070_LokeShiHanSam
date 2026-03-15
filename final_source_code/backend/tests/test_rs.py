import pytest
import os
from pipeline.RS import build_item_text, build_user_text, fit_tfidf, recommend_tfidf


# Test purpose: Ensure that build item text concatenates properly.
# passed successfully
def test_build_item_text_contains_expected_tokens():
    article = {
        "source": {"id": "bbc", "name": "BBC"},
        "title": "Tech update: AI model launch",
        "description": "A breaking tech story",
        "content": "AI model chip gpu startup",
        "_topic": "tech",
        "_style": "breaking",
    }
    s = build_item_text(article)

    assert "Tech update" in s
    assert "source:bbc" in s
    assert "topic:tech" in s
    assert "style:breaking" in s


# Test purpose: ensure that build user text properly flattens user's preference into a single text string
# passed successfully
def test_build_user_text_contains_preferences():
    pref = {
        "preferences": {"sources": ["bbc"], "topics": ["tech"], "style": ["breaking"]}
    }
    s = build_user_text(pref)

    assert "bbc" in s
    assert "tech" in s
    assert "breaking" in s


# Test purpose: Ensure that fit_tfidf returns correct tf_idf matrice shape
# passed successfully
def test_fit_tfidf_returns_expected_shapes():
    articles = [
        {
            "source": {"id": "bbc", "name": "BBC"},
            "title": "Tech update: AI model launch",
            "description": "A breaking tech story about AI",
            "content": "ai model chip gpu startup",
            "_topic": "tech",
            "_style": "breaking",
        },
        {
            "source": {"id": "reuters", "name": "Reuters"},
            "title": "Finance update: markets rally",
            "description": "Stocks and inflation move markets",
            "content": "stock market inflation rates bank",
            "_topic": "finance",
            "_style": "analysis",
        },
    ]

    user_prefs = [
        {
            "preferences": {
                "sources": ["bbc"],
                "topics": ["tech"],
                "style": ["breaking"],
            }
        },
        {
            "preferences": {
                "sources": ["reuters"],
                "topics": ["finance"],
                "style": ["analysis"],
            }
        },
    ]

    tfidf, X_items, X_users = fit_tfidf(articles, user_prefs)

    # Make sure 2 user preferences and 2 articles
    assert X_items.shape[0] == 2
    assert X_users.shape[0] == 2


# Purpose: Ensure that tfidf recommender ranks the most relevant article highest for the user profile
# passed successfully
def test_recommend_tfidf_ranks_best_item_first():
    articles = [
        {
            "source": {"id": "bbc", "name": "BBC"},
            "title": "Tech update: AI model launch",
            "description": "A breaking tech story about AI",
            "content": "ai model chip gpu startup",
            "_topic": "tech",
            "_style": "breaking",
        },
        {
            "source": {"id": "reuters", "name": "Reuters"},
            "title": "Finance update: markets rally",
            "description": "Stocks and inflation move markets",
            "content": "stock market inflation rates bank",
            "_topic": "finance",
            "_style": "analysis",
        },
        {
            "source": {"id": "espn", "name": "ESPN"},
            "title": "Sports update: league finals",
            "description": "A big match",
            "content": "match league goal player tournament",
            "_topic": "sports",
            "_style": "breaking",
        },
    ]

    user_prefs = [
        {
            "preferences": {
                "sources": ["bbc"],
                "topics": ["tech"],
                "style": ["breaking"],
            }
        },
    ]

    _, X_items, X_users = fit_tfidf(articles, user_prefs)

    recs = recommend_tfidf(user_id=0, X_users=X_users, X_items=X_items, N=3)

    # Make sure that rank 0 is index 0, which is the bbc article with the words tech and breaking inside
    assert recs[0] == 0


# Test purpose: ensure that an invalid user indices raises an index error
# passed successfully
def test_recommend_tfidf_invalid_user_id_raises():
    articles = [
        {"source": {"id": "bbc"}, "title": "x", "description": "", "content": ""},
    ]
    user_prefs = [
        {
            "preferences": {
                "sources": ["bbc"],
                "topics": ["tech"],
                "style": ["breaking"],
            }
        },
    ]
    _, X_items, X_users = fit_tfidf(articles, user_prefs)

    # with user id 999 it should fail
    with pytest.raises(IndexError):
        recommend_tfidf(user_id=999, X_users=X_users, X_items=X_items, N=3)
