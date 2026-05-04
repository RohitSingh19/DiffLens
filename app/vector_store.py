import chromadb
from app.embedder import CodeEmbedder


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")

        self.collection = self.client.get_or_create_collection(
            name="code_review_chunks"
        )

        self.embedder = CodeEmbedder()

    def add_chunks(self, chunks: list):
        """
        Store chunks in ChromaDB
        """

        documents = [chunk["content"] for chunk in chunks]
        ids = [chunk["id"] for chunk in chunks]

        metadatas = [
            {
                "file": chunk["file"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"]
            }
            for chunk in chunks
        ]

        embeddings = self.embedder.generate_embeddings(documents)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    def search_similar_code(self, query: str, top_k: int = 3):
        """
        Retrieve semantically similar code chunks
        """

        query_embedding = self.embedder.generate_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results
    
    def search_similar_text(self, query: str, top_k: int = 3):
        results = self.search_similar_code(query, top_k)

        documents = results.get("documents", [[]])[0]

        return documents