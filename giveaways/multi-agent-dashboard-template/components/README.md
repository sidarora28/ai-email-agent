# components/

This directory is for **Streamlit fragment components** — small, reusable UI
pieces you factor out of `app.py` as the dashboard grows.

A "fragment" is a function decorated with [`@st.fragment`](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment)
that reruns independently of the rest of the page. Good candidates:

- `email_card.py` — the per-email card (subject, tags, draft, reviewer verdict)
- `top_bar.py` — the inbox counts + refresh row
- `tag.py` — the small colored category / urgency pill

Keeping these here lets you unit-test rendering logic and reuse it across pages
without bloating `app.py`. In this v0.1 starter everything lives in `app.py` for
readability; refactor into this folder when you start adding screens.
