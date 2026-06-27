"""build_embeddings.py — turn your sent emails into a searchable voice profile.

Reads data/raw_emails.jsonl, embeds each email locally with a small
sentence-transformers model (no API key, runs on your laptop), and stores the
vectors in a local Chroma database at data/embeddings.db.

    python m1-voice/build_embeddings.py

This is a LIVE segment: the audience watches it embed hundreds of emails in
seconds. Everything runs offline.
"""

import json
import os
import time
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_PATH = os.getenv("CHROMA_PATH", "data/embeddings.db")
COLLECTION = os.getenv("CHROMA_COLLECTION", "voice")
RAW = Path("data/raw_emails.jsonl")


def load_emails():
    emails = []
    with RAW.open() as f:
        for line in f:
            line = line.strip()
            if line:
                emails.append(json.loads(line))
    return emails


def main():
    print(f"Loading emails from {RAW} ...")
    emails = load_emails()
    print(f"  {len(emails)} emails to embed")

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print("Connecting to local vector store ...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # fresh build each run so the demo is repeatable
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION)

    print(f"Embedding {len(emails)} emails ...")
    start = time.time()
    texts = [e["body"] for e in emails]
    vectors = model.encode(texts, batch_size=64, show_progress_bar=True)

    collection.add(
        ids=[e["id"] for e in emails],
        embeddings=[v.tolist() for v in vectors],
        documents=texts,
        metadatas=[{"subject": e.get("subject", ""), "to": e.get("to", "")} for e in emails],
    )
    elapsed = time.time() - start

    print(f"Done. Embedded {len(emails)} emails in {elapsed:.1f}s")
    print(f"Voice profile saved to {CHROMA_PATH} (collection: '{COLLECTION}')")


if __name__ == "__main__":
    main()
