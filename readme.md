# Financial Document Q&A Assistant

A small, focused Streamlit app to extract text and tables from financial PDFs/Excel files, index the content with embeddings, and answer questions using a local Ollama model.

This README is written plainly — what I would include when handing in an assignment. No fluff, just the essentials to run and understand the project.

---

## What this project does

- Parse PDFs and Excel files to extract text and tables.
- Chunk the extracted text and build an in-memory embedding index.
- Use a local Ollama instance for embeddings and chat completions.
- Provide a Streamlit UI to ask questions about uploaded documents; answers are based only on document context.

---

## Files (short)

- `app.py` — Streamlit app; handles uploads, processing, indexing, and chat UI.
- `document_parser.py` — Parsing utilities for PDFs/Excel and simple text chunking.
- `embedding_index.py` — Minimal in-memory embedding index and retrieval (cosine similarity).
- `ollama_client.py` — Thin client to call Ollama for embeddings and chat completions.
- `metrics.py` — Small helpers to extract numeric financial metrics from text.
- `requirements.txt` — Python package list used by the project.

---

## Requirements

- Python 3.10+ recommended
- Ollama running locally and reachable (default `http://localhost:11434`)

Install dependencies:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## How to run

1. Ensure Ollama is running locally and the models you plan to use are available.
2. Start the Streamlit app:

```bash
streamlit run app.py
```

3. In the app:
- Upload one or more `.pdf`, `.xlsx`, or `.xls` files.
- Click **Process Documents** to parse and index them.
- Ask questions in the chat box and press **Ask**.

---

## Defaults & where to change them

- Default chat model and embed model names are set in `app.py` and `ollama_client.py`.
- If Ollama is on another URL/port, update `OLLAMA_BASE_URL` inside `ollama_client.py`.
- The retrieval `top_k` default is 5 (adjustable in the app UI).

---

## Troubleshooting

- **Cannot connect to Ollama / port in use**: confirm Ollama is running; change `OLLAMA_BASE_URL` or free the port.
- **Tables not extracted**: scanned PDFs may contain images. This project does not include OCR—use Tesseract or OCR before uploading.
- **Memory issues with many documents**: embeddings are kept in memory. For larger datasets, use a vector DB (FAISS, Milvus) or persist to disk.

---

## Next steps (optional)

- Add `.env` config for Ollama URL and model names.
- Add OCR for scanned PDFs (Tesseract).
- Persist embeddings to a vector store for larger corpora.
- Add tests for parsing and metrics extraction.

---

## License

You can use this for your assignment. If you want a license file, MIT is a simple option.

---

If you want, I can also add a short `git` checklist (commands to commit and push) and a suggested commit message. Tell me if you want that and I’ll add it.

