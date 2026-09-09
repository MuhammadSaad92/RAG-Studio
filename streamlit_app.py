
"""
RAG Studio — Premium chat UI for Employee Policy Q&A
Pipeline: pypdf → all-MiniLM-L6-v2 → Pinecone → Gemini
Run:  streamlit run streamlit_app.py
"""

from __future__ import annotations

import html

import streamlit as st
from services.pipeline_service import ingest_pdf, answer_question

# ============================================================
# Page config — must be the first Streamlit call
# ============================================================
st.set_page_config(
    page_title="RAG Studio · Employee Policy Q&A",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Constants
# ============================================================
AVATAR_USER = "👤"
AVATAR_ASSISTANT = "🤖"

SAMPLE_QUESTIONS = [
    "How many vacation days do I get per year?",
    "What is the remote work policy?",
    "How do I request sick leave?",
    "What benefits does the company offer?",
]

HERO_HTML = """
<div class="hero">
    <div class="hero-badge">✦ &nbsp;Pinecone retrieval × Gemini generation</div>
    <h1 class="hero-title">Ask anything about the Employee Handbook</h1>
    <p class="hero-sub">
        Every answer is grounded in your indexed policy document —
        retrieved via embeddings and cited back to the source chunks.
    </p>
    <div class="feature-strip">
        <span class="feature">⚡ Instant retrieval</span>
        <span class="feature">🔒 Grounded answers</span>
        <span class="feature">📄 Cited sources</span>
    </div>
</div>
"""

# ============================================================
# CSS — modern [data-testid] selectors only (no dead classes)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ---------- Tokens ---------- */
    :root {
        --surface:   rgba(255,255,255,.045);
        --border:    rgba(255,255,255,.08);
        --border-2:  rgba(255,255,255,.16);
        --accent:    #8b5cf6;
        --text:      #eef1f8;
        --text-2:    rgba(238,241,248,.62);
        --text-3:    rgba(238,241,248,.36);
        --r-lg: 20px; --r-md: 14px;
    }

    /* ---------- App background ---------- */
    .stApp {
        font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
        color: var(--text);
        background:
            radial-gradient(1100px 520px at 85% -8%,  rgba(139,92,246,.16), transparent 60%),
            radial-gradient(900px 480px  at -10% 108%, rgba(96,165,250,.12), transparent 55%),
            linear-gradient(168deg, #07070f 0%, #0d0d1f 46%, #0b1428 100%) !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }

    code {
        font-family: 'JetBrains Mono', ui-monospace, Menlo, monospace;
        font-size: .86em;
        background: rgba(255,255,255,.08);
        padding: .12em .45em;
        border-radius: 6px;
    }
    hr { border-color: var(--border) !important; opacity: .7; }
    ::selection { background: rgba(139,92,246,.45); }
    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,.14); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,.26); }
    [data-testid="stCaptionContainer"] { color: var(--text-3) !important; }

    /* ---------- Centered page column ---------- */
    .block-container {
        max-width: 920px !important;
        padding: 2.2rem 1.25rem 8rem !important;   /* bottom padding clears chat input */
        margin-inline: auto !important;
    }
    section[data-testid="stSidebar"] .block-container {
        max-width: 100% !important;
        padding: 1.4rem 1rem 2rem !important;
        margin: 0 !important;
    }

    /* ---------- Hero (empty state) ---------- */
    .hero { text-align: center; padding: 1.6rem 0 .4rem; }
    .hero-badge {
        display: inline-flex; align-items: center; gap: .45rem;
        font-size: .7rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
        color: #c4b5fd; background: rgba(139,92,246,.12);
        border: 1px solid rgba(139,92,246,.3); border-radius: 999px;
        padding: .38rem 1rem; margin-bottom: 1.2rem;
    }
    .hero-title {
        font-size: clamp(1.9rem, 4.5vw, 2.7rem); font-weight: 800;
        line-height: 1.15; margin: 0 0 .9rem;
        background: linear-gradient(100deg, #ffffff 20%, #c4b5fd 55%, #7dd3fc 90%);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub { color: var(--text-2); font-size: .97rem; max-width: 900px; margin: 0 auto; line-height: 1.65; }
    .feature-strip { display: flex; justify-content: center; gap: 1.6rem; flex-wrap: wrap; margin: 1.5rem 0 2rem; }
    .feature { font-size: .8rem; color: var(--text-3); }
    .suggest-label {
        text-align: center; font-size: .72rem; font-weight: 700;
        letter-spacing: .14em; text-transform: uppercase;
        color: var(--text-3); margin: .4rem 0 .9rem;
    }

    /* ---------- Chat messages ---------- */
    [data-testid="stChatMessage"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        padding: 1rem 1.15rem;
        transition: border-color .2s ease;
    }
    [data-testid="stChatMessage"]:hover { border-color: var(--border-2); }
    [data-testid="stChatMessage"] span[class*="chatAvatarIcon"] {
        font-size: 1.45rem !important; background: transparent !important;
    }

    /* User → right-aligned gradient bubble (multi-fallback selectors) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
    [data-testid="stChatMessage"]:has(.chatAvatarIcon-user) {
        background: transparent; border: none; padding: .15rem 0;
        flex-direction: row-reverse;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"]:has(.chatAvatarIcon-user) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        border-radius: 18px 18px 6px 18px;
        padding: .7rem 1.05rem;
        width: fit-content; max-width: 82%; margin-left: auto;
        box-shadow: 0 10px 26px -12px rgba(124,58,237,.6);
    }

    /* ---------- Chat input ---------- */
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important; border: none !important; box-shadow: none !important;
    }
    [data-testid="stChatInput"] > div {
        background: rgba(255,255,255,.055) !important;
        border: 1px solid var(--border-2) !important;
        border-radius: 999px !important;
        backdrop-filter: blur(14px);
        box-shadow: 0 12px 34px -14px rgba(0,0,0,.65);
        transition: border-color .2s ease, box-shadow .2s ease;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: rgba(139,92,246,.6) !important;
        box-shadow: 0 0 0 3px rgba(139,92,246,.18), 0 12px 34px -14px rgba(0,0,0,.65);
    }
    [data-testid="stChatInput"] textarea {
        color: var(--text) !important; font-size: .95rem !important; caret-color: var(--accent);
    }
    [data-testid="stChatInput"] textarea::placeholder { color: var(--text-3) !important; }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
        border-radius: 50% !important; color: #fff !important;
        box-shadow: 0 6px 18px -6px rgba(124,58,237,.7);
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(12,12,26,.92), rgba(8,8,18,.97)) !important;
        border-right: 1px solid var(--border) !important;
    }
    .brand { display: flex; align-items: center; gap: .8rem; padding: .4rem .2rem 1.2rem; }
    .brand-logo {
        width: 44px; height: 44px; border-radius: 14px; flex: none;
        display: flex; align-items: center; justify-content: center; font-size: 1.35rem;
        background: linear-gradient(135deg, rgba(139,92,246,.25), rgba(96,165,250,.15));
        border: 1px solid rgba(139,92,246,.35);
        box-shadow: 0 8px 22px -8px rgba(139,92,246,.5);
    }
    .brand-name { font-weight: 700; font-size: 1.05rem; }
    .brand-sub { font-size: .68rem; color: var(--text-3); letter-spacing: .08em; text-transform: uppercase; margin-top: .12rem; }
    .side-label {
        font-size: .68rem; font-weight: 700; letter-spacing: .14em;
        text-transform: uppercase; color: var(--text-3); margin: 1.1rem 0 .45rem;
    }
    .pill {
        font-size: .75rem; font-weight: 600; border-radius: 999px;
        padding: .5rem .9rem; margin: .2rem 0 .9rem; text-align: center;
    }
    .pill-ok  { background: rgba(52,211,153,.1);  border: 1px solid rgba(52,211,153,.3);  color: #6ee7b7; }
    .pill-warn{ background: rgba(251,191,36,.08); border: 1px solid rgba(251,191,36,.28); color: #fcd34d; }

    /* ---------- Buttons ---------- */
    .stButton > button {
        width: 100%; border-radius: 12px; font-weight: 600; font-size: .88rem;
        padding: .55rem 1rem; color: var(--text) !important;
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        transition: all .2s ease;
    }
    .stButton > button:hover {
        border-color: rgba(139,92,246,.5) !important;
        background: rgba(139,92,246,.1) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
        border: none !important; color: #fff !important;
        box-shadow: 0 8px 22px -8px rgba(124,58,237,.65);
    }
    .stButton > button[kind="primary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {
        filter: brightness(1.12);
        box-shadow: 0 12px 28px -8px rgba(124,58,237,.8);
    }

    /* ---------- Expander (sources) ---------- */
    [data-testid="stExpander"] {
        background: rgba(255,255,255,.03);
        border: 1px solid var(--border) !important;
        border-radius: var(--r-md) !important;
        overflow: hidden; margin-top: .8rem;
    }
    [data-testid="stExpander"] details { background: transparent !important; border: none !important; }
    [data-testid="stExpander"] summary {
        font-size: .84rem; font-weight: 600; color: var(--text-2); padding: .65rem 1rem;
    }
    [data-testid="stExpander"] summary:hover { color: var(--text); }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] { padding: .2rem .9rem .9rem; }

    /* ---------- Source rows ---------- */
    .source-row {
        display: flex; align-items: center; gap: .6rem;
        background: rgba(255,255,255,.03);
        border: 1px solid rgba(255,255,255,.06);
        border-left: 3px solid var(--accent);
        border-radius: 10px; padding: .55rem .8rem; margin-bottom: .45rem;
        font-size: .8rem; color: var(--text-2);
    }
    .source-idx {
        flex: none; width: 20px; height: 20px; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        background: rgba(139,92,246,.18); color: #c4b5fd;
        font-size: .68rem; font-weight: 700;
    }
    .source-name { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .source-score {
        margin-left: auto; flex: none;
        font-size: .68rem; font-weight: 700; letter-spacing: .04em;
        font-family: 'JetBrains Mono', monospace;
        background: rgba(96,165,250,.14); color: #93c5fd;
        border: 1px solid rgba(96,165,250,.25);
        border-radius: 999px; padding: .18rem .6rem;
    }

    /* ---------- Alerts & error chip ---------- */
    [data-testid="stAlert"] {
        background: rgba(255,255,255,.05) !important;
        border: 1px solid var(--border); border-radius: 12px;
    }
    .err-chip {
        background: rgba(248,113,113,.1);
        border: 1px solid rgba(248,113,113,.3);
        color: #fca5a5; border-radius: 12px;
        padding: .6rem .9rem; font-size: .9rem;
    }

    /* ---------- Responsive ---------- */
    @media (max-width: 768px) {
        .block-container { padding: 1.2rem .8rem 7rem !important; }
        .feature-strip { gap: .9rem; }
        [data-testid="stChatMessage"]:has(.chatAvatarIcon-user) [data-testid="stChatMessageContent"] { max-width: 92%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Helpers
# ============================================================
def init_state() -> None:
    """Initialize session state BEFORE any widget touches it (bug fix #1)."""
    for key, value in {
        "messages": [],
        "ingested": False,
        "chunk_count": 0,
        "char_count": 0,
    }.items():
        st.session_state.setdefault(key, value)


def safe_score(value) -> str:
    """Never crash on a missing/None score (bug fix #5)."""
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "—"


def render_sources(sources: list | None) -> None:
    """Render a cited-sources expander. HTML-escaped (bug fix #4)."""
    if not sources:
        return
    with st.expander("📄 View sources"):
        for i, src in enumerate(sources, start=1):
            name = html.escape(str(src.get("source", src.get("id", "unknown"))))
            st.markdown(
                f"""
                <div class="source-row">
                    <span class="source-idx">{i}</span>
                    <span class="source-name">📎 <code>{name}</code></span>
                    <span class="source-score">{safe_score(src.get("score"))}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_history() -> None:
    for msg in st.session_state.messages:
        avatar = AVATAR_USER if msg["role"] == "user" else AVATAR_ASSISTANT
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("error"):
                st.markdown(
                    f'<div class="err-chip">⚠️ {html.escape(str(msg["content"]))}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(str(msg["content"]))
            if msg["role"] == "assistant":
                render_sources(msg.get("sources"))


def handle_prompt(prompt: str, top_k: int) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR_ASSISTANT):
        try:
            with st.spinner("Retrieving context and generating answer…"):
                result = answer_question(prompt, top_k=top_k) or {}
        except Exception as exc:
            # Persist the failure so history stays consistent (bug fix #6)
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Query failed — {exc}", "error": True}
            )
            st.markdown(
                f'<div class="err-chip">⚠️ Query failed — {html.escape(str(exc))}</div>',
                unsafe_allow_html=True,
            )
            return

        answer = str(result.get("answer", "")).strip() or "_No answer was returned._"
        sources = result.get("sources") or []

        st.markdown(answer)
        render_sources(sources)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )


# ============================================================
# App
# ============================================================
init_state()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-logo">🧠</div>
            <div>
                <div class="brand-name">RAG Studio</div>
                <div class="brand-sub">Policy Q&A Engine</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Retrieval</div>', unsafe_allow_html=True)
    top_k = st.slider(
        "Chunks to retrieve (top-K)",
        min_value=1,
        max_value=10,
        value=4,
        help="More chunks = broader context, but can dilute precision.",
    )

    st.markdown('<div class="side-label">Document index</div>', unsafe_allow_html=True)
    if st.session_state.ingested:
        st.markdown(
            f'<div class="pill pill-ok">🟢 Index ready · {st.session_state.chunk_count} chunks</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="pill pill-warn">🟡 Not ingested yet — build the index below</div>',
            unsafe_allow_html=True,
        )

    if st.button("🔄 Rebuild index", type="primary", use_container_width=True):
        try:
            with st.spinner("Extract → chunk → embed → upsert…"):
                result = ingest_pdf() or {}
            st.session_state.ingested = True
            st.session_state.chunk_count = int(result.get("uploaded", 0) or 0)
            st.session_state.char_count = int(result.get("characters", 0) or 0)
            st.toast("Index rebuilt successfully", icon="✅")
            st.success(
                f"Uploaded **{st.session_state.chunk_count}** chunks "
                f"from **{st.session_state.char_count:,}** characters."
            )
        except Exception as exc:
            st.toast("Ingestion failed", icon="🚨")
            st.error(f"Ingestion failed: {exc}")

    st.markdown('<div class="side-label">Session</div>', unsafe_allow_html=True)
    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.toast("Conversation cleared", icon="🧹")
        st.rerun()

    st.divider()
    st.caption(
        "⚡ pypdf → all-MiniLM-L6-v2 → Pinecone → Gemini\n\n"
        "💡 Answers are grounded in the indexed document and cite their sources."
    )

# ---------------- Main chat ----------------
if not st.session_state.messages:
    # Empty state: hero + one-click sample questions
    st.markdown(HERO_HTML, unsafe_allow_html=True)
    st.markdown('<p class="suggest-label">Try one of these</p>', unsafe_allow_html=True)
    cols = st.columns(2, gap="small")
    suggestion = None
    for i, question in enumerate(SAMPLE_QUESTIONS):
        with cols[i % 2]:
            if st.button(question, key=f"sample_{i}", use_container_width=True):
                suggestion = question
else:
    suggestion = None
    render_history()

# chat_input at top level — never nested in columns (bug fix #2)
prompt = st.chat_input("Ask a question about employee policies…")
prompt = prompt or suggestion

if prompt:
    handle_prompt(prompt, top_k=top_k)