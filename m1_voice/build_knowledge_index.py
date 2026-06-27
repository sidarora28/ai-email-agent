"""build_knowledge_index.py — M1 Part 2 (R2.1): the drafter's knowledge index.

Chunks the source-of-truth docs (knowledge/*.md) and embeds them into a local
Chroma index. At draft time the drafter retrieves from here to ground facts
(prices, dates, details) — and may assert nothing that isn't grounded.

    python m1_voice/build_knowledge_index.py
"""

import os
import re
import time
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

KNOWLEDGE_DIR = Path(os.getenv("KNOWLEDGE_DIR", "knowledge"))
INDEX = os.getenv("KNOWLEDGE_INDEX", "data/knowledge_index.db")
MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
COLLECTION = "knowledge"


def chunk_markdown(text, source):
    """Split a markdown doc into chunks by heading; keep each heading with its body."""
    chunks = []
    current_head, buf = source, []
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s", line):
            if buf and any(b.strip() for b in buf):
                chunks.append((current_head, "\n".join(buf).strip()))
            current_head = line.lstrip("#").strip()
            buf = [line]
        else:
            buf.append(line)
    if buf and any(b.strip() for b in buf):
        chunks.append((current_head, "\n".join(buf).strip()))
    # drop placeholder-only chunks
    return [(h, b) for h, b in chunks if b and "Awaiting content" not in b]


def main():
    docs = sorted(KNOWLEDGE_DIR.glob("*.md"))
    print(f"Knowledge docs: {[d.name for d in docs]}")

    items = []
    for d in docs:
        for head, body in chunk_markdown(d.read_text(), d.stem):
            items.append({"source": d.name, "section": head, "text": body})
    print(f"  {len(items)} chunks total")
    if not items:
        print("No content yet — fill knowledge/*.md, then re-run.")
        return

    print(f"Loading model {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=INDEX)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(COLLECTION)

    start = time.time()
    vectors = model.encode([i["text"] for i in items], batch_size=64, show_progress_bar=True)
    col.add(
        ids=[f"{i['source']}#{n}" for n, i in enumerate(items)],
        embeddings=[v.tolist() for v in vectors],
        documents=[i["text"] for i in items],
        metadatas=[{"source": i["source"], "section": i["section"]} for i in items],
    )
    print(f"Done. Knowledge index ({len(items)} chunks) in {time.time()-start:.1f}s -> {INDEX}")


if __name__ == "__main__":
    main()
