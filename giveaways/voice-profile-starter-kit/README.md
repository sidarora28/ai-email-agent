# Voice Profile Starter Kit

Build a searchable **voice profile** from your own sent emails — the foundation
of an AI email assistant that writes like *you*.

You give it your Gmail sent mail; it embeds every email locally and stores them
in a vector database. Then you can hand it any inbound email and instantly pull
up the past replies that sound most like you.

> Everything runs **locally and offline**. The embedding model downloads once,
> then runs on your laptop — **no API key required**. Your emails never leave
> your machine.

---

## Prerequisites

- **Python 3.11+**
- A **Gmail account** (you'll grant read-only access to your sent mail)

---

## Setup (about 5 minutes)

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Gmail OAuth credentials

1. In the [Google Cloud Console](https://console.cloud.google.com/), go to
   **APIs & Services → Credentials**.
2. Create an **OAuth client ID** of type **Desktop app**.
3. Download the JSON and save it as `data/auth/credentials.json`:

```bash
mkdir -p data/auth
mv ~/Downloads/client_secret_*.json data/auth/credentials.json
```

### 4. Extract your sent emails

```bash
python extract_emails.py
```

The first run opens a browser asking you to grant **read-only** Gmail access.
This writes your voice corpus to `data/raw_emails.jsonl`.

### 5. Build the voice profile, then query it

```bash
python build_embeddings.py
python retrieve.py "can you share the course price?"
```

`build_embeddings.py` embeds every email into `data/embeddings.db`.
`retrieve.py` takes any inbound text and returns your most similar past replies.

---

## What this kit gives you vs. what the cohort teaches

**What this kit gives you (v0.1):**
- Pull your sent emails over the Gmail API
- Embed them locally with `sentence-transformers` (no API key)
- A persistent local vector store (Chroma)
- Similarity search: inbound email → your most similar past replies
- Example voice profiles for three personas (`examples/`)

**What the cohort teaches (see `extension-notes.md`):**
- Corpus curation — clean, dedupe, and weight your email corpus
- Re-ranking — reorder retrieval results by true relevance
- Voice evaluation — measure how well a draft sounds like you
- Multi-voice profiles — one person, many personas, routed automatically

> *v0.1 starter. Cohort week 1 teaches corpus curation, re-ranking, voice eval.*

---

## Project layout

```
voice-profile-starter-kit/
├── extract_emails.py     # Gmail sent mail -> data/raw_emails.jsonl
├── build_embeddings.py   # raw_emails.jsonl -> local vector store
├── retrieve.py           # inbound email -> your most similar replies
├── examples/             # synthetic example voice profiles
│   ├── founder/voice.md
│   ├── support/voice.md
│   └── ceo/voice.md
├── extension-notes.md    # where the cohort takes this
├── requirements.txt
├── .env.example          # optional config (sensible defaults built in)
└── .gitignore
```

## Configuration (optional)

Every setting has a sensible default, so the kit runs without any config. To
customize (model, paths, how many emails to pull), copy `.env.example` to `.env`
and edit it.

```bash
cp .env.example .env
```
