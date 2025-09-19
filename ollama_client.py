import requests
from typing import List, Dict, Any

OLLAMA_BASE_URL = "http://localhost:11434"


def embed_texts(texts: List[str], model: str) -> List[List[float]]:
	url = f"{OLLAMA_BASE_URL}/api/embeddings"
	embeddings: List[List[float]] = []
	for t in texts:
		resp = requests.post(url, json={"model": model, "prompt": t}, timeout=120)
		resp.raise_for_status()
		data = resp.json()
		embeddings.append(data.get("embedding", []))
	return embeddings


def chat_completion(model: str, messages: List[Dict[str, Any]]) -> str:
	url = f"{OLLAMA_BASE_URL}/api/chat"
	payload = {"model": model, "messages": messages, "stream": False}
	resp = requests.post(url, json=payload, timeout=180)
	resp.raise_for_status()
	data = resp.json()
	# Ollama chat returns { message: { content: str, role: str } }
	msg = data.get("message", {})
	return msg.get("content", "")
