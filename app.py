import io
import json
from typing import List, Dict, Any

import pandas as pd
import streamlit as st

from document_parser import parse_pdf, parse_excel, chunk_texts
from embedding_index import EmbeddingIndex
from ollama_client import chat_completion
from metrics import extract_metrics_from_texts


APP_TITLE = "Financial Document Q&A Assistant"
DEFAULT_CHAT_MODEL = "llama3.2"
DEFAULT_EMBED_MODEL = "nomic-embed-text"
TOP_K = 5


def initialize_state() -> None:
	if "index" not in st.session_state:
		st.session_state.index = None
	if "docs" not in st.session_state:
		st.session_state.docs = []
	if "tables" not in st.session_state:
		st.session_state.tables = []
	if "messages" not in st.session_state:
		st.session_state.messages = []
	if "metrics" not in st.session_state:
		st.session_state.metrics = {}


def sidebar_controls() -> Dict[str, Any]:
	opts: Dict[str, Any] = {}
	st.sidebar.header("Models")
	opts["chat_model"] = st.sidebar.text_input("Chat model", value=DEFAULT_CHAT_MODEL)
	opts["embed_model"] = st.sidebar.text_input("Embedding model", value=DEFAULT_EMBED_MODEL)

	st.sidebar.header("Retrieval")
	opts["top_k"] = st.sidebar.slider("Top K", 1, 20, TOP_K)

	st.sidebar.header("About")
	st.sidebar.write("Uses local Ollama models. Make sure Ollama is running.")
	return opts


def build_index(uploaded_files: List[Any], embed_model: str) -> None:
	all_texts: List[str] = []
	all_tables: List[pd.DataFrame] = []

	with st.spinner("Parsing documents..."):
		for uf in uploaded_files:
			name = uf.name.lower()
			data = uf.read()
			file_like = io.BytesIO(data)
			if name.endswith(".pdf"):
				texts, tables = parse_pdf(file_like)
				all_texts.extend(texts)
				all_tables.extend(tables)
			elif name.endswith(".xlsx") or name.endswith(".xls"):
				texts, tables = parse_excel(file_like)
				all_texts.extend(texts)
				all_tables.extend(tables)
			else:
				st.warning(f"Unsupported file type: {uf.name}")

		# Chunk long texts to improve retrieval
		all_texts = chunk_texts(all_texts, max_tokens=400)

	with st.spinner("Embedding and indexing..."):
		index = EmbeddingIndex(embed_model=embed_model)
		index.add_documents(all_texts)

	st.session_state.index = index
	st.session_state.docs = all_texts
	st.session_state.tables = all_tables
	st.session_state.metrics = extract_metrics_from_texts(all_texts)


def render_tables() -> None:
	if not st.session_state.tables:
		st.info("No tables extracted.")
		return
	for i, df in enumerate(st.session_state.tables[:5]):
		st.caption(f"Table {i+1}")
		st.dataframe(df, use_container_width=True)


def answer_question(question: str, chat_model: str, top_k: int) -> str:
	if st.session_state.index is None:
		return "Please upload and process documents first."

	retrieved = st.session_state.index.search(question, top_k=top_k)
	context_blocks = [doc for doc, _score in retrieved]
	context = "\n\n".join(context_blocks)
	metrics_json = json.dumps(st.session_state.metrics, indent=2)

	system_prompt = (
		"You are a helpful financial analysis assistant. "
		"Answer using ONLY the provided context from the user's documents. "
		"If the answer isn't in the context, say you don't have enough information. "
		"Prefer numeric answers from tables when possible. Be concise."
	)
	user_prompt = (
		f"Question: {question}\n\n"
		f"Context:\n{context}\n\n"
		f"Extracted metrics (may help):\n{metrics_json}"
	)

	messages = [
		{"role": "system", "content": system_prompt},
		{"role": "user", "content": user_prompt},
	]

	with st.spinner("Thinking..."):
		response = chat_completion(model=chat_model, messages=messages)
	return response


# Streamlit UI
st.set_page_config(page_title=APP_TITLE, page_icon="💼", layout="wide")
st.title(APP_TITLE)

initialize_state()

opts = sidebar_controls()

with st.expander("Upload and Process Documents", expanded=True):
	uploaded = st.file_uploader(
		"Upload PDF or Excel files", type=["pdf", "xlsx", "xls"], accept_multiple_files=True
	)
	col1, col2 = st.columns([1, 1])
	with col1:
		process = st.button("Process Documents", type="primary", use_container_width=True)
	with col2:
		clear = st.button("Clear Session", use_container_width=True)

	if clear:
		st.session_state.index = None
		st.session_state.docs = []
		st.session_state.tables = []
		st.session_state.messages = []
		st.session_state.metrics = {}
		st.success("Session cleared.")

	if process and uploaded:
		try:
			build_index(uploaded, opts["embed_model"])
			st.success("Documents processed and indexed.")
		except Exception as e:
			st.error(f"Processing failed: {e}")

if st.session_state.docs:
	st.subheader("Extracted Tables (preview)")
	render_tables()
	if st.session_state.metrics:
		st.subheader("Auto-Extracted Key Metrics")
		st.json(st.session_state.metrics)

st.subheader("Chat")
user_input = st.text_input("Ask a question about your financials", key="question")
if st.button("Ask") and user_input.strip():
	st.session_state.messages.append({"role": "user", "content": user_input})
	try:
		answer = answer_question(user_input, opts["chat_model"], opts["top_k"])
		st.session_state.messages.append({"role": "assistant", "content": answer})
	except Exception as e:
		st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})

for msg in st.session_state.messages[-10:]:
	if msg["role"] == "user":
		st.chat_message("user").write(msg["content"])
	else:
		st.chat_message("assistant").write(msg["content"])
