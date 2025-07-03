# from sentence_transformers import SentenceTransformer
from openai import OpenAI
from typing import List
import numpy as np
from config import Settings

settings = Settings()

class SortSourceService:
    def __init__(self):
        # self.embedding_model = SentenceTransformer('all-miniLM-L6-v2')
        # openai.api_key = settings.OPENAI_API_KEY
        self.embedding_model = "text-embedding-3-small"
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_embedding(self, text: str):
        # query_embedding = self.embedding_model.encode(query)
        # response = self.client.embeddings.create(
        #     input=[text],
        #     model=self.embedding_model
        # )
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        query_embedding = response.data[0].embedding
        return query_embedding

    def sort_sources(self, query: str, search_results: List[dict]):
        try:
            relevant_docs = []
            query_embedding = self.get_embedding(query)

            for res in search_results:

                if res is None or "content" not in res or res["content"] is None:
                    print(f"Invalid result encountered: {res}")
                    continue

                res_embedding = self.get_embedding(res["content"])
                similarity = float(np.dot(query_embedding, res_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(res_embedding)))

                res["relevant_score"] = similarity

                if similarity > 0.3:
                    relevant_docs.append(res)

            return sorted(relevant_docs, key=lambda x: x["relevant_score"], reverse=True)
        except Exception as e:
            print(e)
