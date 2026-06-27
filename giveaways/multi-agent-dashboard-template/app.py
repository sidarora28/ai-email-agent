"""app.py — the multi-agent Email Assistant dashboard (Streamlit).

Reads classified emails and the drafts produced by orchestrate.py, then shows,
for each inbound email: its category + urgency, the AI-drafted reply, and the
reviewer's verdict. Send / Edit / Skip are display-only (no email is sent).

    streamlit run app.py

Data sources (first that exists wins):
  - classified.json            (drop in your own pre-classified inbox)
  - examples/sample_emails.json (bundled synthetic fallback — renders out of box)
  - drafts.json                (written by orchestrate.py; optional)

If drafts.json is absent the dashboard still renders the inbox; each card just
shows a hint to run orchestrate.py.
"""

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
CLASSIFIED = ROOT / "classified.json"
FALLBACK = ROOT / "examples/sample_emails.json"
DRAFTS = ROOT / "drafts.json"

# Tag colors keyed by category / urgency. Add your own categories here.
CATEGORY_COLORS = {
    "cohort_support": "#4F8DFD",
    "pricing_inquiry": "#22C55E",
    "sponsorship": "#F59E0B",
    "mentorship": "#A78BFA",
    "partnership": "#EC4899",
    "personal": "#94A3B8",
}
URGENCY_COLORS = {"high": "#EF4444", "medium": "#F59E0B", "low": "#64748B"}


def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def load_classified():
    """Prefer a real classified.json; fall back to the bundled synthetic set."""
    if CLASSIFIED.exists():
        return load_json(CLASSIFIED, [])
    return load_json(FALLBACK, [])


def drafts_by_id():
    return {d.get("id"): d for d in load_json(DRAFTS, [])}


def tag(text, color):
    """Render a small pill-shaped colored tag."""
    return (
        f"<span style='background:{color};color:#0B1120;padding:2px 10px;"
        f"border-radius:12px;font-size:12px;font-weight:600'>{text}</span>"
    )


def main():
    st.set_page_config(page_title="Email Assistant", page_icon="📬", layout="wide")

    st.markdown(
        "<h1 style='margin-bottom:0'>📬 Email Assistant</h1>"
        "<p style='color:#94A3B8;margin-top:4px'>Your inbox, triaged and drafted "
        "by a drafter→reviewer agent loop. Review and send.</p>",
        unsafe_allow_html=True,
    )

    emails = load_classified()
    drafts = drafts_by_id()

    if not emails:
        st.info("No emails found. Add classified.json or examples/sample_emails.json.")
        return

    # --- top bar: counts + refresh ---
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    c1.metric("Inbox", len(emails))
    c2.metric("Drafted", len(drafts))
    c3.metric("High urgency", sum(1 for e in emails if e.get("urgency") == "high"))
    if c4.button("🔄 Refresh", use_container_width=True):
        st.rerun()

    st.divider()

    for e in emails:
        cat = e.get("category", "personal")
        urg = e.get("urgency", "low")
        with st.container(border=True):
            head, meta = st.columns([3, 1])
            head.markdown(f"**{e.get('subject','(no subject)')}**")
            head.caption(f"from {e.get('sender','')}")
            meta.markdown(
                tag(cat, CATEGORY_COLORS.get(cat, "#94A3B8")) + " " +
                tag(urg, URGENCY_COLORS.get(urg, "#64748B")),
                unsafe_allow_html=True,
            )

            d = drafts.get(e.get("id"))
            if d:
                left, right = st.columns([3, 2])
                with left:
                    st.markdown("**Drafted reply**")
                    st.text_area(
                        "draft", d.get("draft", ""), height=160,
                        key=f"draft_{e.get('id')}", label_visibility="collapsed",
                    )
                with right:
                    review = d.get("review", {})
                    verdict = review.get("verdict", "—")
                    color = "#22C55E" if verdict == "approve" else "#F59E0B"
                    st.markdown("**Reviewer**")
                    st.markdown(
                        tag(verdict.upper(), color), unsafe_allow_html=True,
                    )
                    st.caption(review.get("comment", ""))
            else:
                st.caption("No draft yet — run `python orchestrate.py`.")

            b1, b2, b3, _ = st.columns([1, 1, 1, 4])
            b1.button("Send", key=f"send_{e.get('id')}", type="primary")
            b2.button("Edit", key=f"edit_{e.get('id')}")
            b3.button("Skip", key=f"skip_{e.get('id')}")


if __name__ == "__main__":
    main()
