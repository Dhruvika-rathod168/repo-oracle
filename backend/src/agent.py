import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import Tool
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.prebuilt import create_react_agent

load_dotenv()

# ── Load vectorstore ───────────────────────────────────────────────────────────
def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        persist_directory=".chroma",
        embedding_function=embeddings
    )

# ── Tools ──────────────────────────────────────────────────────────────────────
def search_codebase(query: str) -> str:
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=5)
    if not docs:
        return "No relevant code found."
    results = []
    for doc in docs:
        meta = doc.metadata
        results.append(
            f"File: {meta.get('file_path', 'unknown')}\n"
            f"Function: {meta.get('name', 'unknown')}\n"
            f"Code:\n{doc.page_content}\n"
        )
    return "\n---\n".join(results)


def find_function(name: str) -> str:
    vectorstore = get_vectorstore()
    all_data    = vectorstore.get()
    results     = []
    for i, metadata in enumerate(all_data["metadatas"]):
        if name.lower() in metadata.get("name", "").lower():
            results.append(
                f"File: {metadata.get('file_path', 'unknown')}\n"
                f"Function: {metadata.get('name', 'unknown')}\n"
                f"Type: {metadata.get('type', 'unknown')}\n"
                f"Lines: {metadata.get('start_line')}–{metadata.get('end_line')}\n"
                f"Code:\n{all_data['documents'][i]}\n"
            )
    if not results:
        return f"No function or class named '{name}' found."
    return "\n---\n".join(results[:5])


def count_chunks(query: str) -> str:
    vectorstore  = get_vectorstore()
    all_data     = vectorstore.get()
    metadatas    = all_data["metadatas"]
    total        = len(metadatas)
    functions    = sum(1 for m in metadatas if m.get("type") == "function")
    classes      = sum(1 for m in metadatas if m.get("type") == "class")
    unique_files = len(set(m.get("file_path", "") for m in metadatas))
    return (
        f"Total chunks: {total}\n"
        f"Functions: {functions}\n"
        f"Classes: {classes}\n"
        f"Files: {unique_files}"
    )


# ── Agent ──────────────────────────────────────────────────────────────────────
def run_agent(question: str) -> str:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )

    tools = [
        Tool(
            name="search_codebase",
            func=search_codebase,
            description=(
                "Semantically search the codebase for relevant code chunks. "
                "Use this for general questions about how something works, "
                "where a feature is implemented, or what a module does. "
                "Input should be a descriptive natural language query. "
                "Example inputs: 'how is authentication handled', 'where is the database connection'"
            )
        ),
        Tool(
            name="find_function",
            func=find_function,
            description=(
                "Find a specific function or class by its exact or partial name. "
                "Use this when the user mentions a specific function, method, or class name. "
                "Also use this to trace how a specific function is defined. "
                "Input should be the function or class name only. "
                "Example inputs: 'Signer', 'sign', 'URLSafeSerializer'"
            )
        ),
        Tool(
            name="count_chunks",
            func=count_chunks,
            description=(
                "Count and summarize the total number of functions, classes, and files "
                "in the indexed codebase. Use this for any counting or statistics questions. "
                "Example inputs: 'how many functions', 'total classes', 'number of files'"
            )
        ),
    ]
    agent = create_react_agent(llm, tools)

    try:
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        last_message = result["messages"][-1]
        return last_message.content
    except Exception as e:
        return f"Agent error: {str(e)}"