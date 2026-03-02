"""
nlp.py
-------------
의미 기반 유사도 추론 엔진 (순수 추론 전용)
"""

from typing import Optional
from sentence_transformers import SentenceTransformer, util

class NLPEngine:
    _instance: Optional["NLPEngine"] = None

    def __init__(self, model_name: str = "jhgan/ko-sroberta-multitask"):
        print(f"⏳ NLPEngine: 모델 로딩 중... ({model_name})")
        self.model = SentenceTransformer(model_name)
        print("✅ NLPEngine: 로딩 완료")

    @classmethod
    def get_instance(cls, model_name: str = "jhgan/ko-sroberta-multitask") -> "NLPEngine":
        if cls._instance is None:
            cls._instance = cls(model_name)
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def find_best_match(self, target_text: str, candidates: list[dict], threshold: float = 0.5) -> Optional[dict]:
        if not candidates:
            return None

        candidate_texts = [c["text"] for c in candidates]
        target_emb = self.model.encode(target_text, convert_to_tensor=True)
        cand_embs  = self.model.encode(candidate_texts, convert_to_tensor=True)
        scores     = util.cos_sim(target_emb, cand_embs)[0]

        best_idx      = scores.argmax().item()
        best_score    = scores[best_idx].item()
        best_candidate = candidates[best_idx]

        if best_score < threshold:
            print(f"❌ [NLP] '{target_text}' 의미 매칭 실패 (최고 유사도: {best_score:.2f})")
            return None

        is_exact = best_score >= 0.99
        print(f"🧠 [NLP] '{target_text}' → '{best_candidate['text']}' "
              f"({'정확 일치' if is_exact else f'의미 추론: {best_score:.2f}'})")

        best_candidate["nlp_score"] = best_score
        return best_candidate

    def semantic_score(self, text_a: str, text_b: str) -> float:
        if not text_a or not text_b:
            return 0.0
        emb_a = self.model.encode(text_a, convert_to_tensor=True)
        emb_b = self.model.encode(text_b, convert_to_tensor=True)
        return float(util.cos_sim(emb_a, emb_b)[0][0])