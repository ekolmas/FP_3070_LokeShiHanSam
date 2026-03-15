import json
import os
import sys
from pathlib import Path
import traceback
from dotenv import load_dotenv

# Comment the following imports if running unit tests
from RS import fit_tfidf, recommend_tfidf
from LLM import generate_conversation_for_article
from TTS import generate_audio

# Comment the following imports if running full system
# from pipeline.RS import fit_tfidf, recommend_tfidf
# from pipeline.LLM import generate_conversation_for_article
# from pipeline.TTS import generate_audio

load_dotenv()

# Get env variables for model endpoint and API key
# Set default fields in case env variables are missing
DEFAULT_MODEL_ENDPOINT = os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.5-air:free")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OUTPUT_DIR = os.getenv("TTS_OUTPUT_DIR", "tts_output")

# IMPORTANT Set variables to reduce verbosity of transformers and tokenizers that clutters the stdout output that nodejs reads
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# Function purpose: to emit messages to the stdout for NodeJS to read and update the UI in real time as each article is processed
def emit(obj: dict):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


# Function purpose: to read JSON from stdin (NodeJS) and convert to python dict
# Parse stdin using json.loads, and handle any invalid JSONs
def _read_stdin_json():
    raw_output = sys.stdin.read()
    # Check if the input is empty
    if not raw_output.strip():
        raise ValueError("no input received")
    # Try to parse the input as JSON
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parsing error: {e}")


# Function purpose: create a safe id for an article for audio output path naming
# if there is an article id from NewsAPI use it otherwise use last part of url, otherwise use title or a fallback index
def _safe_article_id(article, fallback_index):
    # use article id if it exists
    if article.get("id"):
        return str(article["id"])

    # use last part of url if it exists, limit to 60 char
    url = article.get("url")
    if url:
        tail = url.rstrip("/").split("/")[-1]
        if tail:
            return tail[:60]

    # if all fails, use title
    title = article.get("title")

    # if title is missing, use a fallback id
    if not title:
        title = "article_" + str(fallback_index)

    safe = ""

    # replace all non alphanumeric characters with underscores
    for ch in title:
        if ch.isalnum():
            safe += ch
        else:
            safe += "_"

    # remove trailing underscores
    safe = safe.strip("_")

    # limit id length to 60
    if len(safe) > 60:
        safe = safe[:60]

    # Final fallback if something went wrong
    if not safe:
        safe = "article_" + str(fallback_index)

    return str(fallback_index) + "_" + safe


# Function purpose: Run the full pipeline, including recommend top articles, generate LLM conversations, generate TTS audio then returning structured results to nodejs via stdout
# This is the main function that is used by node js and orchestrates the AI models used.
def run_pipeline(payload):
    # get the article and user preference from payload
    articles = payload.get("articles") or []
    user_pref = payload.get("user_pref") or {}

    # Ensure that the article and user preference fields are not empty
    if not isinstance(articles, list) or len(articles) == 0:
        raise ValueError("article is empty")
    if not isinstance(user_pref, dict) or "preferences" not in user_pref:
        raise ValueError("user preference is empty")

    # get model endpoint from payload
    model_endpoint = payload.get("model_endpoint") or DEFAULT_MODEL_ENDPOINT

    # ensure that the openapi key is not missing before doing anything
    if OPENROUTER_API_KEY is None:
        raise ValueError("open router api key missing")

    # Recommender System
    # print("Starting Recommmender system")
    user_prefs = [user_pref]

    _, X_items, X_users = fit_tfidf(articles, user_prefs)
    ranked_ids = recommend_tfidf(user_id=0, X_users=X_users, X_items=X_items)

    top_articles = [articles[i] for i in ranked_ids]

    print("ranked_ids:", ranked_ids, file=sys.stderr)
    print("len(articles):", len(articles), file=sys.stderr)

    # LLM conversation generator
    # print("Starting LLM conversation generator")
    conversations = []
    # Generate a conversation for each article
    for i, article in zip(ranked_ids, top_articles):
        convo = generate_conversation_for_article(
            model_endpoint=model_endpoint,
            article=article,
            openrouter_api_key=OPENROUTER_API_KEY,
        )
        conversations.append((i, article, convo))

    # TTS Podcast audio generation
    # print("Starting text to speech generation")
    results = []
    # Generate audio for each article
    for rank, (idx, article, convo) in enumerate(conversations, start=1):
        article_id = _safe_article_id(article, fallback_index=idx)

        final_audio_path = generate_audio(
            article_id=article_id,
            conversation=convo,
        )

        # append the audio and conversation to return at the end
        results.append(
            {
                "rank": rank,
                "item_index": int(idx),
                "article_id": article_id,
                "title": article.get("title"),
                "source": (article.get("source") or {}).get("id"),
                "url": article.get("url"),
                "image_url": article.get("urlToImage"),
                "audio_path": str(Path(final_audio_path).resolve()),
                "conversation": convo,
            }
        )

        emit({"type": "item_ready", "item": results[-1]})

    podcast_id = results[0]["article_id"] if results else "podcast"
    podcast_title = results[0]["title"] if results else "Daily Podcast"
    image_url = results[0]["image_url"] if results else None

    emit(
        {
            "type": "done",
            "podcast_id": podcast_id,
            "podcast_title": podcast_title,
            "image_url": image_url,
        }
    )

    # return the results
    return {
        "ok": True,
        "model_endpoint": model_endpoint,
        "recommended": results,
    }


# Function purpose: entry point for command line that reads the stdin payload from nodejs, runs the  pipeline and prints the JSON output for NodeJS
# Implements a command line wrapper that reads stdin, processes using run_pipeline and returns using stdout Json.
def main():
    try:
        # Read JSON payload from stdin sent by NodeJS
        payload = _read_stdin_json()
        # Run the pipeline with the payload
        run_pipeline(payload)
        sys.exit(0)
    except Exception as e:
        emit({"type": "error", "error": str(e)})
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
