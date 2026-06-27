"""retrieve.py — find the past replies that sound most like a given email.

Given an inbound email (on stdin or as a string), embeds it with the same model
and returns your top-K most similar past replies from the voice profile.

    python m1-voice/retrieve.py < data/sample_inbound.txt
    python m1-voice/retrieve.py "can you share the course price?"

Also exposes retrieve_similar(text, k=5) for import by M2/M3.
Runs fully offline against the local Chroma DB.
"""

import os
import sys
from functools import lru_cache

# The model is already cached by build_embeddings.py, so load it from disk and
# never touch the network mid-demo. This also satisfies "works fully offline".
# (Override by exporting HF_HUB_OFFLINE=0 if you ever need a fresh download.)
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_PATH = os.getenv("CHROMA_PATH", "data/embeddings.db")
COLLECTION = os.getenv("CHROMA_COLLECTION", "voice")
DEFAULT_K = int(os.getenv("RETRIEVE_K", "5"))


@lru_cache(maxsize=1)
def _model():
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def _collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_collection(COLLECTION)


def retrieve_similar(text, k=DEFAULT_K):
    """Return up to k past replies most similar to `text`.

    Each result: {"text", "subject", "to", "score"} (score: 1.0 = identical).
    """
    vector = _model().encode([text])[0].tolist()
    res = _collection().query(query_embeddings=[vector], n_results=k)
    out = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        out.append({
            "text": doc,
            "subject": meta.get("subject", ""),
            "to": meta.get("to", ""),
            "score": round(1 - dist, 3),
        })
    return out


def main():
    arg = " ".join(sys.argv[1:]).strip()
    text = arg if arg else sys.stdin.read().strip()
    if not text:
        print("Provide an inbound email via stdin or as an argument.")
        return

    print(f"Inbound:\n  {text[:200]}\n")
    print(f"Top {DEFAULT_K} replies that sound like you:\n")
    for i, r in enumerate(retrieve_similar(text, DEFAULT_K), 1):
        print(f"[{i}] (match {r['score']}) re: {r['subject'][:50]}")
        print(f"    {r['text'][:160]}\n")


if __name__ == "__main__":
    main()
