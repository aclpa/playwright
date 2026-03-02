"""
nlp_engine.py
-------------
의미 기반 유사도 추론 엔진.

주요 개선사항:
  1. 싱글톤 패턴 — 모델을 한 번만 로드
  2. 검증된 데이터만 Triplet으로 저장 (오염 방지)
  3. self_healing.py와 연결되는 인터페이스 제공
"""

import json
from pathlib import Path
from typing import Optional
from sentence_transformers import SentenceTransformer, util


class NLPEngine:
    """
    SentenceTransformer 기반 의미 유사도 추론 엔진.
    싱글톤으로 관리되어 모델을 프로세스 내 1회만 로드합니다.
    """

    _instance: Optional["NLPEngine"] = None

    def __init__(self, model_name: str = "jhgan/ko-sroberta-multitask"):
        print(f"⏳ NLPEngine: 모델 로딩 중... ({model_name})")
        self.model = SentenceTransformer(model_name)
        print("✅ NLPEngine: 로딩 완료")

        # Triplet 데이터 저장 경로
        self.dataset_dir = Path("datasets/nlp")
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        self.triplet_file = self.dataset_dir / "collected_triplets.json"
        if not self.triplet_file.exists():
            with open(self.triplet_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    @classmethod
    def get_instance(cls, model_name: str = "jhgan/ko-sroberta-multitask") -> "NLPEngine":
        """싱글톤 인스턴스 반환. 최초 1회만 모델을 로드합니다."""
        if cls._instance is None:
            cls._instance = cls(model_name)
        return cls._instance

    @classmethod
    def reset(cls):
        """테스트 격리가 필요할 때 인스턴스를 초기화합니다."""
        cls._instance = None

    # ------------------------------------------------------------------
    # 핵심 추론
    # ------------------------------------------------------------------

    def find_best_match(
        self,
        target_text: str,
        candidates: list[dict],
        threshold: float = 0.5,
        confirmed: Optional[bool] = None,
    ) -> Optional[dict]:
        """
        target_text와 의미적으로 가장 가까운 후보를 반환합니다.

        Parameters
        ----------
        target_text : 찾으려는 텍스트 (예: "Dashboard")
        candidates  : [{"text": "홈", "coords": (cx, cy)}, ...]
        threshold   : 이 점수 미만이면 None 반환
        confirmed   : 외부에서 선택 결과가 맞았는지 여부 전달
                      True  → Triplet에 positive로 저장
                      False → Triplet에 hard negative로 저장
                      None  → 저장 보류 (나중에 confirm()으로 결정)

        Returns
        -------
        가장 유사한 후보 dict, 또는 None
        """
        if not candidates:
            return None

        candidate_texts = [c["text"] for c in candidates]

        # 임베딩 및 코사인 유사도 계산
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
        print(
            f"🧠 [NLP] '{target_text}' → '{best_candidate['text']}' "
            f"({'정확 일치' if is_exact else f'의미 추론: {best_score:.2f}'})"
        )

        # ── Triplet 데이터 수집 ───────────────────────────────────────
        # 글자가 다른 경우(의미 추론이 발동된 경우)만 저장 대상
        if not is_exact:
            negatives = [c["text"] for i, c in enumerate(candidates) if i != best_idx]

            if confirmed is True:
                # 외부에서 "맞았다"고 확인된 경우 → 즉시 저장
                self._save_triplet(
                    anchor=target_text,
                    positive=best_candidate["text"],
                    negatives=negatives,
                    verified=True,
                )
            elif confirmed is False:
                # 외부에서 "틀렸다"고 확인된 경우 → hard negative로 저장
                self._save_triplet(
                    anchor=target_text,
                    positive=None,          # 정답을 모름
                    negatives=[best_candidate["text"]] + negatives,
                    verified=False,
                )
            else:
                # confirmed=None: 저장 보류, pending 상태로 기록
                self._save_triplet(
                    anchor=target_text,
                    positive=best_candidate["text"],
                    negatives=negatives,
                    verified=False,         # 미검증 상태
                )

        best_candidate["nlp_score"] = best_score
        return best_candidate

    def semantic_score(self, text_a: str, text_b: str) -> float:
        """
        두 텍스트 간 의미 유사도를 0.0~1.0으로 반환.
        self_healing.py의 앙상블 계산에서 사용합니다.
        """
        if not text_a or not text_b:
            return 0.0
        emb_a = self.model.encode(text_a, convert_to_tensor=True)
        emb_b = self.model.encode(text_b, convert_to_tensor=True)
        return float(util.cos_sim(emb_a, emb_b)[0][0])

    def confirm_last_match(self, anchor: str, was_correct: bool):
        """
        테스트 실행 후 AI가 추론한 결과가 맞았는지 외부에서 알려주는 함수.
        pending 상태의 Triplet을 verified=True/False로 업데이트합니다.

        사용 예시:
            # 클릭 후 페이지가 정상 이동했으면 correct=True
            nlp.confirm_last_match("Dashboard", was_correct=True)
        """
        try:
            with open(self.triplet_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 가장 최근에 저장된 anchor 항목 업데이트
            for entry in reversed(data):
                if entry["anchor"] == anchor and not entry.get("verified", False):
                    entry["verified"] = was_correct
                    break

            with open(self.triplet_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"⚠️ [NLP] confirm 업데이트 실패: {e}")

    # ------------------------------------------------------------------
    # Triplet 데이터 저장
    # ------------------------------------------------------------------

    def _save_triplet(
        self,
        anchor: str,
        positive: Optional[str],
        negatives: list[str],
        verified: bool,
    ):
        """
        Triplet 데이터를 JSON에 누적합니다.

        저장 구조:
        {
            "anchor":   "삭제",
            "positive": "Remove",       # None이면 정답 미확인
            "negatives": ["취소", "확인"],
            "verified": true            # False면 미검증 — 학습에 사용 금지
        }
        """
        try:
            with open(self.triplet_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            entry = {
                "anchor":    anchor,
                "positive":  positive,
                "negatives": negatives,
                "verified":  verified,
            }
            data.append(entry)

            with open(self.triplet_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            status = "✅ verified" if verified else "⏳ pending"
            print(f"💾 [NLP] Triplet 저장 [{status}]: {anchor} → {positive}")

        except Exception as e:
            print(f"⚠️ [NLP] Triplet 저장 실패: {e}")

    def get_verified_triplets(self) -> list[dict]:
        """검증된 Triplet만 반환 (Fine-tuning 학습용)."""
        try:
            with open(self.triplet_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            verified = [d for d in data if d.get("verified") and d.get("positive")]
            print(f"📊 [NLP] 검증된 Triplet: {len(verified)}개 / 전체: {len(data)}개")
            return verified
        except Exception:
            return []