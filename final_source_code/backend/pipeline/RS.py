import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


# Function purpose: build text representation of an article for content based tfidf recommender
# Does this by concatenating structured and unstructured data into text string
def build_item_text(article):
    return " ".join(
        [
            article.get("title") or "",
            article.get("description") or "",
            article.get("content") or "",
            f"source:{(article.get('source') or {}).get('id','')}",
            f"topic:{article.get('_topic','')}",
            f"style:{article.get('_style','')}",
        ]
    ).strip()


# Function purpose: build user preference profile into text representation that is compatible with the article vectors
# Does this by flattening user preference into a text string
def build_user_text(user_pref):
    prefs = user_pref.get("preferences", {})
    sources = prefs.get("sources", []) or []
    topics = prefs.get("topics", []) or []
    styles = prefs.get("style", []) or []

    return " ".join(
        [
            " ".join(sources),
            " ".join(topics),
            " ".join(styles),
        ]
    ).strip()


# Function purpose: Fit tfidf feature space and embed articles and user preference in it
# Fits TF-IDF vectorizer on the item texts. Projects items and users into the same vector space
def fit_tfidf(articles, user_prefs):
    item_texts = [build_item_text(a) for a in articles]
    user_texts = [build_user_text(p) for p in user_prefs]

    tfidf = TfidfVectorizer(
        max_features=20000, ngram_range=(1, 2), stop_words="english"
    )

    X_items = tfidf.fit_transform(item_texts)
    X_users = tfidf.transform(user_texts)

    return tfidf, X_items, X_users


# Function purpose: Rank and recommend articles for articles that is most relevant to a user's preference
# Computes cosine similarity between user and item tf idf vectors and returns the top N items
def recommend_tfidf(user_id: int, X_users, X_items, N=1):
    sims = linear_kernel(X_users[user_id], X_items).ravel()

    if N <= 0:
        return []

    # Sort all items by score descending
    ranked = np.argsort(-sims)

    # Remove filtered items (-inf) and return up to N
    ranked = [int(i) for i in ranked if np.isfinite(sims[i])]
    return ranked[: min(N, len(ranked))]
