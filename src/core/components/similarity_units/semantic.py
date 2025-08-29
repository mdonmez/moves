from fastembed import TextEmbedding
import numpy as np

from data.models import SimilarityResult, Chunk


class Semantic:
    def __init__(self) -> None:
        self.model = TextEmbedding(
            model_name="sentence-transformers/all-MiniLM-l6-v2",
            specific_model_path="src/core/components/ml_models/all-MiniLM-L6-v2_quint8_avx2",
        )

    def compare(
        self, input_str: str, candidates: list[Chunk]
    ) -> list[SimilarityResult]:
        try:
            embedding_input = [input_str] + [
                candidate.partial_content for candidate in candidates
            ]

            embeddings = list(self.model.embed(embedding_input))

            input_embedding = embeddings[0]
            candidate_embeddings = embeddings[1:]

            cosine_scores = np.dot(candidate_embeddings, input_embedding)

            results = [
                SimilarityResult(chunk=candidate, score=float(score))
                for candidate, score in zip(candidates, cosine_scores)
            ]
            results.sort(key=lambda x: x.score, reverse=True)
            return results

        except Exception as e:
            raise RuntimeError(f"Semantic similarity comparison failed: {e}") from e


if __name__ == "__main__":
    input_text = "the weather is sunny today"
    candidates = [
        Chunk(partial_content="It's a bright and sunny day.", source_sections=[]),
        Chunk(partial_content="The rain is pouring down.", source_sections=[]),
    ]

    semantic = Semantic()
    results = semantic.compare(input_text, candidates)

    for result in results:
        print(f"Candidate: {result.chunk.partial_content}, Score: {result.score}")
