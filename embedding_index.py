from typing import List, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ollama_client import embed_texts


class EmbeddingIndex:
	def __init__(self, embed_model: str):
		self.embed_model = embed_model
		self.documents: List[str] = []
		self.embeddings: np.ndarray | None = None

	def add_documents(self, docs: List[str]) -> None:
		if not docs:
			return
		embs = embed_texts(docs, model=self.embed_model)
		self.documents.extend(docs)
		if self.embeddings is None:
			self.embeddings = np.array(embs, dtype=np.float32)
		else:
			self.embeddings = np.vstack([self.embeddings, np.array(embs, dtype=np.float32)])

	def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
		if self.embeddings is None or not self.documents:
			return []
		q_emb = embed_texts([query], model=self.embed_model)[0]
		q_emb = np.array(q_emb, dtype=np.float32).reshape(1, -1)
		sims = cosine_similarity(q_emb, self.embeddings)[0]
		idxs = np.argsort(-sims)[:top_k]
		return [(self.documents[i], float(sims[i])) for i in idxs]
