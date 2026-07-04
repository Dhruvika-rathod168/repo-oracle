import os
import streamlit as st
from src.ingestion import ingest_repo
from src.embeddings import create_vectorstore, load_vectorstore
from src.retrieval import retrieve_chunks
from src.generation import generate_answer

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Codebase Q&A Assistant", page_icon="⚡", layout="wide")

# ── Session state ──────────────────────────────────────────────────────────────
if "vectorstore"   not in st.session_state: st.session_state.vectorstore   = None
if "messages"      not in st.session_state: st.session_state.messages      = []
if "repo_url"      not in st.session_state: st.session_state.repo_url      = ""
if "repo_name"     not in st.session_state: st.session_state.repo_name     = ""
if "dark_mode"     not in st.session_state: st.session_state.dark_mode     = False
if "show_map"      not in st.session_state: st.session_state.show_map      = False
if "chunks"        not in st.session_state: st.session_state.chunks        = []
if "selected_file" not in st.session_state: st.session_state.selected_file = None

# ── Theme ──────────────────────────────────────────────────────────────────────
if st.session_state.dark_mode:
    BG         = "#000000"
    SIDEBAR_BG = "#000000"
    BORDER     = "#0f2760"
    TEXT       = "#ffffff"
    SUBTEXT    = "#ffffff"
    CARD_BG    = "#18264d"
    INPUT_BG   = "#000000"
else:
    BG         = "#000000"
    SIDEBAR_BG = "#000000"
    BORDER     = "#0f2760"
    TEXT       = "#ffffff"
    SUBTEXT    = "#ffffff"
    CARD_BG    = "#18264d"
    INPUT_BG   = "#000000"

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {BG}; }}
  [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; border-right: 0.5px solid {BORDER}; }}
  html, body, [class*="css"] {{ color: {TEXT}; }}
  .stTextInput > div > div > input {{
    background-color: {INPUT_BG}; border: 0.5px solid {BORDER};
    border-radius: 10px; color: {TEXT};
  }}
  .stButton > button {{
    background-color: #16213e ; color: white; border: none;
    border-radius: 10px; width: 100%; font-weight: 500;
  }}

  .stButton > button:hover {{ background-color: #6F89E0; }}
  .stChatInput > div {{ background-color: {INPUT_BG}; border: 0.5px solid {BORDER}; border-radius: 24px; }}
  [data-testid="stChatMessage"] {{
    background-color: {CARD_BG}; border: 0.5px solid {BORDER};
    border-radius: 14px; color: {TEXT};
  }}
 
  #MainMenu, footer {{ visibility: hidden; }}
  header {{ visibility: visible; }}

  /* Repo map styles */
  .map-container {{
    background: {CARD_BG}; border: 0.5px solid {BORDER};
    border-radius: 14px; padding: 20px;
  }}
  .map-col {{
    background: {BG}; border: 0.5px solid {BORDER};
    border-radius: 12px; padding: 14px;
  }}
  .file-item {{
    padding: 5px 10px; border-radius: 6px; cursor: pointer;
    font-size: 13px; color: {TEXT};
  }}
  .file-item:hover {{ background: {SIDEBAR_BG}; }}
  .file-item.active {{
    background: {SIDEBAR_BG}; border-left: 2px solid #7c6fff;
    color: #7c6fff;
  }}
  .fn-item {{
    padding: 8px 10px; border-radius: 8px;
    border: 0.5px solid {BORDER}; background: {BG};
    margin-bottom: 6px; font-size: 12px;
  }}
  .fn-name {{ font-family: monospace; color: {TEXT}; }}
  .fn-type {{
    font-size: 10px; color: #7c6fff;
    background: {SIDEBAR_BG}; padding: 1px 6px;
    border-radius: 10px; display: inline-block; margin-top: 3px;
  }}
  .fn-line {{ font-size: 11px; color: {SUBTEXT}; }}

</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
      <div style="width:26px;height:26px;border-radius:8px;
                  background:linear-gradient(135deg,#1a1aff,#0099ff);
                  display:flex;align-items:center;justify-content:center;
                  font-size:13px;color:#fff;">⚡</div>
      <span style="font-size:18px;font-weight:500;color:{TEXT};">CodebaseRAG</span>
    </div>

    <hr style="border:0.5px solid {BORDER};margin-bottom:8px;">
        
    """, unsafe_allow_html=True) 

    st.session_state.dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

    st.markdown(f"<div style='font-size:11px;color:{SUBTEXT};text-transform:uppercase;"
                f"letter-spacing:0.08em;font-weight:500;margin-bottom:8px;'>Repository</div>",
                unsafe_allow_html=True)

    repo_url = st.text_input("GitHub repo URL", value=st.session_state.repo_url,
                              placeholder="https://github.com/<username>/<repository>.git")

    if st.button("⚡ Index Repository"):
        if not repo_url.strip():
            st.warning("Please enter a GitHub repository URL.")
        else:
            with st.spinner("Indexing repository..."):
                chunks = ingest_repo(repo_url.strip())
                create_vectorstore(chunks)
                st.session_state.vectorstore  = load_vectorstore()
                st.session_state.repo_url     = repo_url.strip()
                st.session_state.repo_name    = repo_url.strip().split("/")[-1].replace(".git", "")
                st.session_state.chunks       = chunks
                st.session_state.selected_file = None
                st.session_state.show_map     = False
            st.success("✓ Indexed successfully")

    if st.session_state.repo_name:
        # count unique files and chunks
        unique_files = list(set(c["file_path"] for c in st.session_state.chunks))
        st.markdown(f"""
        <div style="background:{BG};border:0.5px solid {BORDER};border-radius:10px;padding:12px;margin-top:4px;">
          <div style="font-size:13px;color:{TEXT};font-weight:500;">{st.session_state.repo_name}</div>
          <div style="font-size:11px;color:#7c6fff;margin-top:4px;">Python · indexed</div>
          <div style="display:flex;gap:8px;margin-top:8px;">
            <span style="font-size:11px;color:#7c6fff;background:{SIDEBAR_BG};
                         padding:3px 8px;border-radius:20px;border:0.5px solid {BORDER};">
              {len(st.session_state.chunks)} chunks
            </span>
            <span style="font-size:11px;color:#7c6fff;background:{SIDEBAR_BG};
                         padding:3px 8px;border-radius:20px;border:0.5px solid {BORDER};">
              {len(unique_files)} files
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

        # Toggle between map and chat
        if st.session_state.show_map:
            if st.button("💬 Back to Chat"):
                st.session_state.show_map = False
                st.rerun()
        else:
            if st.button("🗺️ View Repo Map"):
                st.session_state.show_map = True
                st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="padding-bottom:12px;border-bottom:0.5px solid {BORDER};margin-bottom:16px;">
  <div style="font-size:26px;font-weight:600;color:{TEXT};display:flex;align-items:center;gap:10px;">
    Codebase Q&amp;A Assistant
  
  </div>
  <div style="font-size:13px;color:{SUBTEXT};margin-top:4px;">
    {'Browse the indexed files and functions below.' if st.session_state.show_map
     else 'Explore the repo map first, then ask codebase questions.'}
  </div>
</div>
""", unsafe_allow_html=True)

# ── REPO MAP VIEW ──────────────────────────────────────────────────────────────
if st.session_state.show_map:
    if not st.session_state.chunks:
        st.warning("No repo indexed yet. Please index a repository first.")
    else:
        # Build file → chunks mapping
        file_map = {}
        for chunk in st.session_state.chunks:
            fp = chunk["file_path"]
            if fp not in file_map:
                file_map[fp] = []
            file_map[fp].append(chunk)

        col1, col2 = st.columns([1, 1.5])

        # ── Left: File Tree ──
        with col1:
            st.markdown(f"""
            <div style="font-size:11px;color:{SUBTEXT};text-transform:uppercase;
                        letter-spacing:0.08em;font-weight:500;margin-bottom:10px;">
              📂 File Tree
            </div>
            """, unsafe_allow_html=True)

            search_file = st.text_input("", placeholder="🔍 Search files...", key="file_search")

            for fp in sorted(file_map.keys()):
                display = os.path.basename(fp)
                if search_file.lower() in display.lower():
                    is_active = st.session_state.selected_file == fp
                    bg = "#7c6fff" if is_active else "#1a1a2e"
                    st.markdown(f"""
                    <style>
                    div[data-testid="stButton"] button[key="file_{fp}"] {{
                        background-color: {bg} !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                    if st.button(f" {display}", key=f"file_{fp}", use_container_width=True):
                        st.session_state.selected_file = fp
                        st.rerun()

        # ── Right: Function List ──
        with col2:
            selected = st.session_state.selected_file
            if not selected:
                st.markdown(f"""
                <div style="color:{SUBTEXT};font-size:13px;margin-top:40px;text-align:center;">
                  ← Select a file to see its functions and classes
                </div>
                """, unsafe_allow_html=True)
            else:
                fname = os.path.basename(selected)
                st.markdown(f"""
                <div style="font-size:11px;color:{SUBTEXT};text-transform:uppercase;
                            letter-spacing:0.08em;font-weight:500;margin-bottom:10px;">
                  ⚡ Functions &amp; Classes — {fname}
                </div>
                """, unsafe_allow_html=True)

                search_fn = st.text_input("", placeholder="🔍 Search functions...", key="fn_search")

                for chunk in file_map[selected]:
                    name = chunk.get("name", "unknown")
                    ctype = chunk.get("type", "function")
                    start = chunk.get("start_line", "?")
                    end   = chunk.get("end_line", "?")

                    if search_fn.lower() in name.lower():
                        st.markdown(f"""
                        <div class="fn-item">
                          <div class="fn-name">{name}</div>
                          <div style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                            <span class="fn-type">{ctype}</span>
                            <span class="fn-line">line {start}–{end}</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

# ── CHAT VIEW ──────────────────────────────────────────────────────────────────
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("  Ask a question about the indexed codebase")
    if question:
        if st.session_state.vectorstore is None:
            st.warning("⚠️ Please index a repository first.")
        else:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    retrieved = retrieve_chunks(question, st.session_state.vectorstore)
                    answer    = generate_answer(question, retrieved)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})