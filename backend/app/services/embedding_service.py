import time
import math
import random
import logging
import concurrent.futures
from typing import List
from app.config import settings

logger = logging.getLogger("talk_to_your_notes.embedding")


class EmbeddingService:

    def __init__(self, model_name: str = None, dimension: int = 768):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.dimension = dimension or settings.EMBEDDING_DIMENSION

    def embed_text(self, text: str) -> List[float]:
        results = self.embed_documents([text])
        return results[0] if results else self._generate_mock_embedding(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # Attempt to use live Google Gemini API if configured with valid format
        if (
            settings.GEMINI_API_KEY
            and not settings.GEMINI_API_KEY.startswith("mock")
            and settings.GEMINI_API_KEY.startswith("AIzaSy")
        ):
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)

                def call_api(text: str):
                    return genai.embed_content(
                        model=f"models/{self.model_name}",
                        content=text,
                        task_type="retrieval_document"
                    )

                embeddings = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    futures = [executor.submit(call_api, t) for t in texts]
                    for f in futures:
                        # 4 second timeout per embedding API request
                        response = f.result(timeout=4.0)
                        if "embedding" in response and response["embedding"]:
                            vec = response["embedding"]
                            if len(vec) > self.dimension:
                                vec = vec[:self.dimension]
                            elif len(vec) < self.dimension:
                                vec = vec + [0.0] * (self.dimension - len(vec))
                            embeddings.append(vec)

                if len(embeddings) == len(texts):
                    return embeddings
            except Exception as e:
                logger.warning(f"Gemini API Embedding failed: {e}. Falling back to deterministic embedding vector.")

        # Fallback to deterministic pseudo-embeddings for testing/offline/dev mode
        return [self._generate_mock_embedding(t) for t in texts]

    def _generate_mock_embedding(self, text: str) -> List[float]:
        seed = sum(ord(c) for c in text)
        rng = random.Random(seed)
        vec = [rng.gauss(0, 1) for _ in range(self.dimension)]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]
