import streamlit as st
from src.ingestion import ingest_repo
from src.embeddings import create_vectorstore, load_vectorstore
from src.retrieval import retrieve_chunks
from src.generation import generate_answer

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Codebase Q&A Assistant", page_icon="⚡", layout="wide")

# ── Session state ──────────────────────────────────────────────────────────────
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "repo_url" not in st.session_state:
    st.session_state.repo_url = ""
if "repo_name" not in st.session_state:
    st.session_state.repo_name = ""
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ── Theme colors ───────────────────────────────────────────────────────────────
if st.session_state.dark_mode:
    BG         = "#09090f"
    SIDEBAR_BG = "#0f0d1a"
    BORDER     = "#1e1a30"
    TEXT       = "#c4b8f0"
    SUBTEXT    = "#3d3560"
    BUBBLE_BOT = "#0f0d1a"
    BUBBLE_BOT_TEXT = "#c4b8f0"
    CODE_BG    = "#09090f"
    CODE_TEXT  = "#a78bfa"
    CITE_BG    = "#09090f"
    INPUT_BG   = "#0f0d1a"
    STAT_BG    = "#0f0d1a"
else:
    BG         = "#ffffff"
    SIDEBAR_BG = "#f3f0fc"
    BORDER     = "#e0daf7"
    TEXT       = "#3d3460"
    SUBTEXT    = "#a89fc8"
    BUBBLE_BOT = "#f9f8ff"
    BUBBLE_BOT_TEXT = "#3d3460"
    CODE_BG    = "#f3f0fc"
    CODE_TEXT  = "#7c6fff"
    CITE_BG    = "#f3f0fc"
    INPUT_BG   = "#f9f8ff"
    STAT_BG    = "#f3f0fc"

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* Page background */
  .stApp {{ background-color: {BG}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG};
    border-right: 0.5px solid {BORDER};
  }}

  /* All text */
  html, body, [class*="css"] {{ color: {TEXT}; }}

  /* Inputs */
  .stTextInput > div > div > input {{
    background-color: {INPUT_BG};
    border: 0.5px solid {BORDER};
    border-radius: 10px;
    color: {TEXT};
  }}

  /* Primary button */
  .stButton > button {{
    background-color: #7c6fff;
    color: white;
    border: none;
    border-radius: 10px;
    width: 100%;
    font-weight: 500;
  }}
  .stButton > button:hover {{ background-color: #6a5de8; }}

  /* Chat input */
  .stChatInput > div {{
    background-color: {INPUT_BG};
    border: 0.5px solid {BORDER};
    border-radius: 24px;
  }}

  /* Chat messages */
  [data-testid="stChatMessage"] {{
    background-color: {BUBBLE_BOT};
    border: 0.5px solid {BORDER};
    border-radius: 14px;
    color: {BUBBLE_BOT_TEXT};
  }}

  /* Hide default streamlit header */
  #MainMenu, footer, header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
      <div style="width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,#7c6fff,#a855f7);
                  display:flex;align-items:center;justify-content:center;font-size:13px;color:#fff;">⚡</div>
      <span style="font-size:14px;font-weight:500;color:{TEXT};">CodebaseRAG</span>
    </div>
    <hr style="border:0.5px solid {BORDER};margin-bottom:8px;">
    """, unsafe_allow_html=True)

    # Dark mode toggle
    st.session_state.dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

    st.markdown(f"<div style='font-size:11px;color:{SUBTEXT};text-transform:uppercase;letter-spacing:0.08em;font-weight:500;margin-bottom:8px;'>Repository</div>", unsafe_allow_html=True)

    repo_url = st.text_input("GitHub repo URL", value=st.session_state.repo_url,
                              placeholder="https://github.com/pallets/flask")

    if st.button("⚡ Index Repository"):
        if not repo_url.strip():
            st.warning("Please enter a GitHub repository URL.")
        else:
            with st.spinner("Indexing repository..."):
                chunks = ingest_repo(repo_url.strip())
                create_vectorstore(chunks)
                st.session_state.vectorstore = load_vectorstore()
                st.session_state.repo_url = repo_url.strip()
                st.session_state.repo_name = repo_url.strip().split("/")[-1].replace(".git", "")
            st.success("✓ Indexed successfully")

    # Repo info card
    if st.session_state.repo_name:
        st.markdown(f"""
        <div style="background:{BG};border:0.5px solid {BORDER};border-radius:10px;padding:12px;margin-top:4px;">
          <div style="font-size:13px;color:{TEXT};font-weight:500;">{st.session_state.repo_name}</div>
          <div style="font-size:11px;color:#7c6fff;margin-top:4px;">Python · indexed</div>
        </div>
        """, unsafe_allow_html=True)

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="padding-bottom:12px;border-bottom:0.5px solid {BORDER};margin-bottom:16px;">
  <div style="font-size:22px;font-weight:600;color:{TEXT};display:flex;align-items:center;gap:10px;">
    Codebase Q&amp;A Assistant
    <span style="font-size:11px;background:{SIDEBAR_BG};color:#7c6fff;padding:3px 10px;
                 border-radius:20px;border:0.5px solid {BORDER};font-weight:400;">
      Repo map first · Q&amp;A second
    </span>
  </div>
  <div style="font-size:13px;color:{SUBTEXT};margin-top:4px;">
    Explore the repo map first, then ask codebase questions.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
question = st.chat_input("Ask a question about the indexed codebase")
if question:
    if st.session_state.vectorstore is None:
        st.warning("⚠️ Please index a repository first.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                retrieved_chunks = retrieve_chunks(question, st.session_state.vectorstore)
                answer = generate_answer(question, retrieved_chunks)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})