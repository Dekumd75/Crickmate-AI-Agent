import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class RAGEngine:

    def __init__(self):
        base = os.path.dirname(__file__)

        self.doc_path = os.path.join(base, "rag_store", "documents")
        self.db_path  = os.path.join(base, "rag_store", "embeddings")

        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        self.index_file = os.path.join(self.db_path, "vector.index")
        self.text_file  = os.path.join(self.db_path, "db.json")

        self.text_chunks = []
        self.index = None

        self._load_if_exists()


    def _load_if_exists(self):
        import json

        if os.path.exists(self.text_file):
            self.text_chunks = json.load(open(self.text_file, "r"))

        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
        else:
            self.index = faiss.IndexFlatL2(384)


    def index_documents(self):
        import json

        files = os.listdir(self.doc_path)

        for fname in files:
            full = os.path.join(self.doc_path, fname)

            if not fname.lower().endswith(".txt"):
                continue

            text = open(full, "r", encoding="utf-8").read()

            chunks = text.split("\n")

            for c in chunks:
                c = c.strip()
                if len(c) < 5:
                    continue

                emb = self.model.encode([c])

                self.index.add(np.array(emb).astype("float32"))
                self.text_chunks.append(c)

        with open(self.text_file, "w") as f:
            json.dump(self.text_chunks, f, indent=2)

        faiss.write_index(self.index, self.index_file)
        return True


    def ask(self, query, top_k=3):
        q_vec = self.model.encode([query])
        q_vec = np.array(q_vec).astype("float32")

        D, I = self.index.search(q_vec, top_k)

        results = []
        for idx in I[0]:
            results.append(self.text_chunks[idx])

        return results
