# simple in-memory "vector store" stub for future FAISS/pgvector swap
from collections import deque


class Memory:
    def __init__(self, max_items=1000):
        self.buf = deque(maxlen=max_items)

    def upsert(self, evt: dict, feats: dict):
        self.buf.append({"evt": evt, "feats": feats})

    def topk(self, query_feats: dict, k: int = 5):
        # placeholder: return last k for now
        return list(self.buf)[-k:]
