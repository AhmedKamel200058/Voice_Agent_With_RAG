import os
import numpy as np
from typing import List

# PDF + Text split
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss


class RAGEngine:
    def __init__(self, knowledge_path="knowledge"):
        self.knowledge_path = knowledge_path

        # Load embedding model
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        # Load documents
        self.documents = self.load_all_pdfs()

        # Convert to embeddings
        self.embeddings = self.encoder.encode(self.documents)

        # Build FAISS index
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(self.embeddings)

        print(f"[RAG] Loaded {len(self.documents)} chunks from PDFs.")

    # ----------------------------------------------------------------------
    # LOAD PDFS
    # ----------------------------------------------------------------------
    def load_pdf(self, file_path: str) -> List[str]:
        reader = PdfReader(file_path)
        all_text = ""

        for page in reader.pages:
            all_text += page.extract_text() + "\n"

        # basic chunking
        chunk_size = 350
        chunks = [all_text[i:i + chunk_size] for i in range(0, len(all_text), chunk_size)]
        return chunks

    def load_all_pdfs(self) -> List[str]:
        all_docs = []

        for file in os.listdir(self.knowledge_path):
            if file.endswith(".pdf"):
                path = os.path.join(self.knowledge_path, file)
                print(f"[RAG] Loading PDF: {file}")
                chunks = self.load_pdf(path)
                all_docs.extend(chunks)

        return all_docs

    # ----------------------------------------------------------------------
    # RAG RETRIEVAL
    # ----------------------------------------------------------------------
    def rag_answer(self, query: str) -> str:
        q_emb = self.encoder.encode([query])

        scores, index = self.index.search(q_emb, 3)
        retrieved = [self.documents[i] for i in index[0]]

        context = "\n\n".join(retrieved)

        return (
            f"Relevant Knowledge Retrieved:\n{context}\n\n"
            "Use this information to answer the user."
        )
