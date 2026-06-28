"use client";

import { useEffect, useMemo, useState } from "react";

const fmtConf = (c) => (c == null ? "" : `${Math.round(c * 100)}% conf`);
const routeLabel = { draft: "→ draft", needs_human: "needs you", skip: "automated" };

export default function Page() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(() => new Set());
  const [draftingIds, setDraftingIds] = useState(() => new Set());
  const [approving, setApproving] = useState(() => new Set());
  const [edited, setEdited] = useState({});
  const [showSkipped, setShowSkipped] = useState(false);
  const [toast, setToast] = useState("");

  async function loadInbox() {
    setError("");
    try {
      const res = await fetch("/api/inbox", { cache: "no-store" });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setItems(data);
    } catch (e) {
      setError(String(e.message || e));
      setItems([]);
    }
  }

  useEffect(() => {
    loadInbox();
  }, []);

  const { actionable, skipped } = useMemo(() => {
    const list = items || [];
    return {
      actionable: list.filter((i) => i.route !== "skip"),
      skipped: list.filter((i) => i.route === "skip"),
    };
  }, [items]);

  function toggle(id) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  function selectSuggested() {
    const ids = actionable
      .filter((i) => i.route === "draft" && i.status !== "approved")
      .map((i) => i.id);
    setSelected(new Set(ids));
  }

  async function writeDrafts() {
    const ids = [...selected];
    if (!ids.length) return;
    setDraftingIds(new Set(ids));
    setError("");
    try {
      const res = await fetch("/api/draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      await loadInbox();
      setSelected(new Set());
      setToast(`Drafted ${ids.length} ${ids.length === 1 ? "reply" : "replies"}`);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setDraftingIds(new Set());
    }
  }

  async function approve(item) {
    setApproving((p) => new Set(p).add(item.id));
    setError("");
    try {
      const body = edited[item.id] ?? item.draft ?? "";
      const res = await fetch("/api/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: item.id, body }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setItems((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, status: "approved", draft: body } : i))
      );
      setToast("Added to your Gmail Drafts — never sent");
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setApproving((p) => {
        const n = new Set(p);
        n.delete(item.id);
        return n;
      });
    }
  }

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 3200);
    return () => clearTimeout(t);
  }, [toast]);

  const busy = draftingIds.size > 0;

  return (
    <div className="wrap">
      <div className="header">
        <div>
          <h1 className="title">Email Assistant</h1>
          <p className="subtitle">
            Pick which emails to reply to — it drafts in your voice, a reviewer checks each
            one, and nothing sends until you approve.
          </p>
        </div>
        <div className="header-actions">
          <button className="btn btn-sm" onClick={loadInbox} disabled={busy}>
            Refresh
          </button>
        </div>
      </div>

      <hr className="divider" />

      {error && <div className="banner-err">{error}</div>}

      {items === null && <div className="loading">Loading your inbox…</div>}

      {items && items.length === 0 && !error && (
        <div className="empty">
          No classified emails yet.
          <br />
          Run <code>bash fetch-emails.sh</code> then <code>bash categorize-emails.sh</code> first.
        </div>
      )}

      {actionable.length > 0 && (
        <>
          <div className="section-label">Inbox · {actionable.length}</div>
          {actionable.map((item) => {
            const isDrafting = draftingIds.has(item.id);
            const isApproving = approving.has(item.id);
            const hasDraft = item.status === "drafted" || item.status === "approved";
            const rev = item.review || {};
            return (
              <div
                key={item.id}
                className={"card" + (selected.has(item.id) ? " selected" : "")}
              >
                <div className="card-top">
                  <input
                    type="checkbox"
                    className="checkbox"
                    checked={selected.has(item.id)}
                    onChange={() => toggle(item.id)}
                    disabled={item.status === "approved" || isDrafting}
                    aria-label="select email"
                  />
                  <div className="card-main">
                    <div className="row1">
                      <span className="sender">{item.sender}</span>
                      <span className="conf">{fmtConf(item.confidence)}</span>
                    </div>
                    <div className="subject">{item.subject || "(no subject)"}</div>
                    {item.snippet && <div className="snippet">{item.snippet}</div>}

                    <div className="chips">
                      {item.category && <span className="chip cat">{item.category}</span>}
                      {item.urgency && <span className="chip">{item.urgency} urgency</span>}
                      <span className={"badge " + item.route}>{routeLabel[item.route]}</span>
                      {item.intent && <span className="chip">{item.intent}</span>}
                    </div>

                    {isDrafting && (
                      <div className="drafting-row">
                        <span className="spinner" /> drafting in your voice…
                      </div>
                    )}

                    {item.status === "insufficient_info" && (
                      <div className="draft-panel">
                        <span className="note">
                          No draft — not enough grounded info. {rev.comment}
                        </span>
                      </div>
                    )}
                    {item.status === "error" && (
                      <div className="draft-panel">
                        <span className="note">Couldn’t draft: {rev.comment}</span>
                      </div>
                    )}

                    {hasDraft && !isDrafting && (
                      <div className="draft-panel">
                        <div className="review-chips">
                          {rev.verdict && (
                            <span className={"verdict " + rev.verdict}>
                              {rev.verdict === "approve" ? "✓ reviewer approved" : "↻ revised"}
                            </span>
                          )}
                          <span className="check">
                            grounded{" "}
                            <span className={rev.grounded ? "ok" : "no"}>
                              {rev.grounded ? "✓" : "✗"}
                            </span>
                          </span>
                          <span className="check">
                            voice{" "}
                            <span className={rev.voice_match ? "ok" : "no"}>
                              {rev.voice_match ? "✓" : "✗"}
                            </span>
                          </span>
                          {rev.comment && <span className="review-comment">“{rev.comment}”</span>}
                        </div>

                        <textarea
                          className="draft-text"
                          value={edited[item.id] ?? item.draft ?? ""}
                          onChange={(e) =>
                            setEdited((p) => ({ ...p, [item.id]: e.target.value }))
                          }
                          readOnly={item.status === "approved"}
                        />

                        <div className="draft-actions">
                          {item.status === "approved" ? (
                            <span className="approved-pill">✓ In your Gmail Drafts</span>
                          ) : (
                            <>
                              <button
                                className="btn btn-approve btn-sm"
                                onClick={() => approve(item)}
                                disabled={isApproving}
                              >
                                {isApproving ? (
                                  <>
                                    <span className="spinner" /> approving…
                                  </>
                                ) : (
                                  "Approve → Gmail draft"
                                )}
                              </button>
                              <span className="note">Creates a draft. Never sends.</span>
                            </>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </>
      )}

      {skipped.length > 0 && (
        <>
          <div className="section-label">
            <button className="btn-ghost btn-sm" onClick={() => setShowSkipped((s) => !s)}>
              {showSkipped ? "Hide" : "Show"} automated / skipped · {skipped.length}
            </button>
          </div>
          {showSkipped &&
            skipped.map((item) => (
              <div key={item.id} className="card muted">
                <div className="card-top">
                  <div className="card-main">
                    <div className="row1">
                      <span className="sender">{item.sender}</span>
                    </div>
                    <div className="subject">{item.subject || "(no subject)"}</div>
                    <div className="chips">
                      {item.category && <span className="chip">{item.category}</span>}
                      <span className="badge skip">automated</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
        </>
      )}

      <div className="actionbar">
        <div className="actionbar-inner">
          <span className="sel-count">
            {selected.size} selected
            {actionable.some((i) => i.route === "draft" && i.status !== "approved") && (
              <>
                {" · "}
                <button className="btn-ghost btn-sm" onClick={selectSuggested} disabled={busy}>
                  Select suggested
                </button>
              </>
            )}
          </span>
          <button
            className="btn btn-primary"
            onClick={writeDrafts}
            disabled={busy || selected.size === 0}
          >
            {busy ? (
              <>
                <span className="spinner" /> Drafting {draftingIds.size}…
              </>
            ) : (
              `✍️  Write ${selected.size || ""} ${selected.size === 1 ? "draft" : "drafts"}`
            )}
          </button>
        </div>
      </div>

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
