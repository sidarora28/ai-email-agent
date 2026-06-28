"""retrieve.py — query the M1 indexes at runtime (voice + knowledge).

Loaded from disk, offline (the model is cached by the M1 build scripts).
"""

import logging
import os
import warnings
from functools import lru_cache

# model is cached from M1 builds; never touch the network mid-run
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
# keep the terminal clean for the live demo (no telemetry/warning noise)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore")
# chromadb's telemetry logs "Failed to send telemetry event ..." regardless of the
# env var (a posthog version bug). Silence its loggers outright.
for _n in ("chromadb", "chromadb.telemetry", "chromadb.telemetry.product.posthog"):
    logging.getLogger(_n).setLevel(logging.CRITICAL)

import chromadb  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

load_dotenv()

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VOICE_INDEX = os.getenv("VOICE_INDEX", "data/voice_index.db")
KNOWLEDGE_INDEX = os.getenv("KNOWLEDGE_INDEX", "data/knowledge_index.db")


@lru_cache(maxsize=1)
def _model():
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=2)
def _collection(path, name):
    client = chromadb.PersistentClient(
        path=path, settings=chromadb.Settings(anonymized_telemetry=False))
    return client.get_collection(name)


def _query(path, name, text, k):
    vec = _model().encode([text])[0].tolist()
    res = _collection(path, name).query(query_embeddings=[vec], n_results=k)
    out = []
    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        out.append({"text": doc, "meta": meta})
    return out


def retrieve_voice(text, k=3):
    """Sid's closest past replies (doc = reply body; meta has incoming_subject/body)."""
    return _query(VOICE_INDEX, "voice", text, k)


def retrieve_knowledge(text, k=4):
    """Closest knowledge chunks (doc = chunk text; meta has source/section)."""
    return _query(KNOWLEDGE_INDEX, "knowledge", text, k)
