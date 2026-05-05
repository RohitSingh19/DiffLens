from openai import OpenAI
import os

class CodeEmbedder:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_embedding(self, text: str):
        """
        Generate embedding for a single chunk
        """
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def generate_embeddings(self, texts: list[str]):
        """
        Generate embeddings for multiple chunks
        """
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]