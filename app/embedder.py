from sentence_transformers import SentenceTransformer


class CodeEmbedder:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_embedding(self, text: str):
        """
        Generate embedding for a single chunk
        """
        return self.model.encode(text).tolist()

    def generate_embeddings(self, texts: list[str]):
        """
        Generate embeddings for multiple chunks
        """
        return self.model.encode(texts).tolist()