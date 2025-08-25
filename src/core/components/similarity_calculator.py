from .similarity_units.phonetic import Phonetic
from .similarity_units.semantic import Semantic

from ...data.models import Chunk, SimilarityResult


class SimilarityCalculator:
    def __init__(self, semantic_weight: float = 0.4, phonetic_weight: float = 0.6):
        self.semantic_weight = semantic_weight
        self.phonetic_weight = phonetic_weight
        self.semantic = Semantic()
        self.phonetic = Phonetic()

    def _normalize_scores(self, results: list[SimilarityResult]) -> dict[int, float]:
        if not results:
            return {}

        valid_scores = [res.score for res in results if res.score >= 0.5]
        if not valid_scores:
            return {id(res.chunk): 0.0 for res in results}

        min_val = min(valid_scores)
        max_val = max(valid_scores)

        if max_val == min_val:
            return {id(res.chunk): 1.0 if res.score >= 0.5 else 0.0 for res in results}

        score_range = max_val - min_val

        normalized = {}
        for res in results:
            if res.score >= 0.5:
                normalized[id(res.chunk)] = (res.score - min_val) / score_range
            else:
                normalized[id(res.chunk)] = 0.0

        return normalized

    def compare(
        self, input_str: str, candidates: list[Chunk]
    ) -> list[SimilarityResult]:
        if not candidates:
            return []

        try:
            semantic_results = self.semantic.compare(input_str, candidates)
            phonetic_results = self.phonetic.compare(input_str, candidates)

            semantic_norm = self._normalize_scores(semantic_results)
            phonetic_norm = self._normalize_scores(phonetic_results)

            final_results = []
            for candidate in candidates:
                candidate_id = id(candidate)
                sem_score = semantic_norm.get(candidate_id, 0.0)
                pho_score = phonetic_norm.get(candidate_id, 0.0)

                weighted_score = (
                    self.semantic_weight * sem_score + self.phonetic_weight * pho_score
                )

                final_results.append(
                    SimilarityResult(chunk=candidate, score=weighted_score)
                )

            final_results.sort(key=lambda x: x.score, reverse=True)

            return final_results

        except Exception as e:
            raise RuntimeError(f"Similarity comparison failed: {e}") from e


if __name__ == "__main__":
    import time

    calculator = SimilarityCalculator(semantic_weight=0.4, phonetic_weight=0.6)

    input_text = "That's write."
    candidates = [
        Chunk(partial_content="That's right.", source_sections=[]),
        Chunk(partial_content="The write stuff.", source_sections=[]),
    ]
    start_time = time.time()
    results = calculator.compare(input_str=input_text, candidates=candidates)
    end_time = time.time()

    for result in results:
        print(f"Candidate: {result.chunk.partial_content}, Score: {result.score}")

    print(f"Similarity calculation time: {(end_time - start_time) * 1000:.2f}ms")
