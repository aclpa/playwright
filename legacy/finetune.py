"""
finetune.py
-----------
NLP 모델 Triplet Loss Fine-tuning 파이프라인.

3단계 구조:
  1. 시드 데이터 생성  — ERP UI 도메인 특화 Triplet을 코드로 직접 정의
  2. 수집 데이터 병합  — collected_triplets.json (healer 실전 수집분)
  3. Fine-tuning 실행  — SentenceTransformer Triplet Loss 학습

실행:
  python utils/finetune.py             # 전체 파이프라인
  python utils/finetune.py --dry-run   # 데이터 확인만 (학습 없음)
  python utils/finetune.py --seed-only # 시드 데이터만으로 학습
"""

import json
import math
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

import torch
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader


# ──────────────────────────────────────────────────────────────────────────────
# 1. 시드 데이터 — ERP UI 도메인 특화 Triplet
#    구조: (anchor, positive, negative)
#    원칙: negative는 실제로 혼동될 수 있는 "Hard Negative"만 사용
# ──────────────────────────────────────────────────────────────────────────────

SEED_TRIPLETS = [
    # ── 생성/저장 계열 ─────────────────────────────────────────────
    ("저장",       "Save",         "취소"),
    ("저장",       "등록",         "수정"),
    ("저장",       "확인",         "닫기"),
    ("Create",     "생성",         "Delete"),
    ("Create",     "New",          "Cancel"),
    ("New Issue",  "이슈 생성",    "이슈 목록"),
    ("New Project","프로젝트 생성","프로젝트 삭제"),
    ("New Sprint", "스프린트 생성","스프린트 종료"),
    ("New Team",   "팀 생성",      "팀 삭제"),
    ("작성",       "등록",         "삭제"),
    ("작성",       "저장",         "취소"),
    ("Submit",     "제출",         "Reset"),
    ("Submit",     "등록",         "취소"),

    # ── 삭제 계열 ──────────────────────────────────────────────────
    ("삭제",       "Delete",       "취소"),
    ("삭제",       "Remove",       "확인"),
    ("Delete",     "삭제",         "Edit"),
    ("Remove",     "삭제",         "Add"),

    # ── 수정/편집 계열 ─────────────────────────────────────────────
    ("수정",       "Edit",         "삭제"),
    ("수정",       "Update",       "Cancel"),
    ("Edit",       "편집",         "Delete"),
    ("Edit Profile","프로필 수정", "프로필 삭제"),
    ("Update",     "업데이트",     "Revert"),
    ("UPDATE",     "저장",         "취소"),

    # ── 취소/닫기 계열 ─────────────────────────────────────────────
    ("취소",       "Cancel",       "확인"),
    ("취소",       "닫기",         "저장"),
    ("Cancel",     "취소",         "Submit"),
    ("닫기",       "Close",        "열기"),

    # ── 확인 계열 ──────────────────────────────────────────────────
    ("확인",       "OK",           "취소"),
    ("확인",       "Confirm",      "Cancel"),

    # ── 내비게이션 ─────────────────────────────────────────────────
    ("Dashboard",  "대시보드",     "Settings"),
    ("Dashboard",  "Home",         "Profile"),
    ("Home",       "홈",           "로그아웃"),
    ("Projects",   "프로젝트",     "Issues"),
    ("Issues",     "이슈",         "Sprint"),
    ("Sprints",    "스프린트",     "Teams"),
    ("Teams",      "팀",           "Profile"),
    ("Profile",    "프로필",       "Logout"),
    ("Kanban",     "칸반",         "Dashboard"),

    # ── 로그인/로그아웃 계열 ───────────────────────────────────────
    ("로그인",     "Login",        "로그아웃"),
    ("로그인",     "Sign In",      "Sign Up"),
    ("로그아웃",   "Logout",       "로그인"),
    ("Logout",     "로그아웃",     "Login"),

    # ── 상태 변경 계열 ─────────────────────────────────────────────
    ("Active",     "활성",         "Inactive"),
    ("Inactive",   "비활성",       "Active"),
    ("완료",       "Done",         "진행중"),
    ("진행중",     "In Progress",  "완료"),
    ("To Do",      "할 일",        "Done"),

    # ── 검색/필터 ──────────────────────────────────────────────────
    ("검색",       "Search",       "필터"),
    ("Search",     "검색",         "Filter"),
    ("Filter",     "필터",         "Sort"),

    # ── 멤버/팀 관련 ───────────────────────────────────────────────
    ("Members",    "멤버",         "Projects"),
    ("Add Member", "멤버 추가",    "멤버 삭제"),
    ("Owner",      "소유자",       "Member"),
]


# ──────────────────────────────────────────────────────────────────────────────
# 파이프라인 클래스
# ──────────────────────────────────────────────────────────────────────────────

class TripletFineTuner:
    """
    NLP 모델 Fine-tuning 파이프라인.

    사용 예시:
        tuner = TripletFineTuner()
        tuner.run()
    """

    def __init__(
        self,
        base_model: str = "jhgan/ko-sroberta-multitask",
        output_dir: str = "models/nlp_finetuned",
        triplet_file: str = "datasets/nlp/collected_triplets.json",
        epochs: int = 10,
        batch_size: int = 16,
        warmup_ratio: float = 0.1,
        min_verified: int = 10,       # verified 데이터 최소 기준
    ):
        self.base_model   = base_model
        self.output_dir   = Path(output_dir)
        self.triplet_file = Path(triplet_file)
        self.epochs       = epochs
        self.batch_size   = batch_size
        self.warmup_ratio = warmup_ratio
        self.min_verified = min_verified

        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 메인 파이프라인
    # ------------------------------------------------------------------

    def run(self, dry_run: bool = False, seed_only: bool = False):
        """
        전체 파이프라인 실행.

        dry_run   : 데이터 통계만 출력, 학습 없음
        seed_only : 시드 데이터만으로 학습 (collected_triplets 무시)
        """
        print("\n" + "=" * 60)
        print("  🧠 Triplet Fine-tuning 파이프라인 시작")
        print("=" * 60)

        # ── Step 1: 데이터 수집 ───────────────────────────────────────
        seed_data      = self._load_seed_data()
        collected_data = [] if seed_only else self._load_collected_data()

        all_triplets = seed_data + collected_data
        self._print_stats(seed_data, collected_data)

        if dry_run:
            print("\n[dry-run] 학습을 건너뜁니다.")
            return

        if not all_triplets:
            print("\n❌ 학습 데이터가 없습니다.")
            return

        # ── Step 2: 데이터 품질 경고 ─────────────────────────────────
        verified_count = len(collected_data)
        if verified_count < self.min_verified and not seed_only:
            print(
                f"\n⚠️  verified 수집 데이터가 {verified_count}개입니다. "
                f"({self.min_verified}개 미만)\n"
                f"   시드 데이터 {len(seed_data)}개로만 학습합니다."
            )
            all_triplets = seed_data

        # ── Step 3: Fine-tuning 실행 ─────────────────────────────────
        model_path = self._finetune(all_triplets)

        # ── Step 4: 검증 ─────────────────────────────────────────────
        self._validate(model_path)

        print("\n✅ Fine-tuning 완료!")
        print(f"   모델 저장 경로: {model_path}")
        print(f"   nlp.py에서 사용하려면:")
        print(f"   NLPEngine.get_instance(model_name='{model_path}')\n")

    # ------------------------------------------------------------------
    # Step 1: 데이터 로드
    # ------------------------------------------------------------------

    def _load_seed_data(self) -> list[InputExample]:
        """시드 Triplet → InputExample 변환."""
        examples = []
        for anchor, positive, negative in SEED_TRIPLETS:
            examples.append(InputExample(texts=[anchor, positive, negative]))
        print(f"📦 시드 데이터: {len(examples)}개")
        return examples

    def _load_collected_data(self) -> list[InputExample]:
        """
        collected_triplets.json에서 verified=True인 데이터만 로드.
        positive가 없거나 verified=False인 데이터는 제외.
        """
        if not self.triplet_file.exists():
            print("📦 수집 데이터: 0개 (파일 없음)")
            return []

        with open(self.triplet_file, "r", encoding="utf-8") as f:
            raw = json.load(f)

        examples = []
        skipped  = 0

        for entry in raw:
            # verified=True이고 positive가 있는 것만 사용
            if not entry.get("verified", False):
                skipped += 1
                continue
            if not entry.get("positive"):
                skipped += 1
                continue

            anchor   = entry["anchor"]
            positive = entry["positive"]
            negatives = entry.get("negatives", [])

            if not negatives:
                # negative가 없으면 시드에서 임의 negative 하나 보충
                negatives = [self._find_fallback_negative(anchor)]

            # negative가 여러 개면 각각 별도 InputExample로 생성 (데이터 증강)
            for neg in negatives[:3]:  # 최대 3개로 제한
                examples.append(InputExample(texts=[anchor, positive, neg]))

        print(f"📦 수집 데이터: {len(examples)}개 사용 / {skipped}개 스킵 (미검증)")
        return examples

    @staticmethod
    def _find_fallback_negative(anchor: str) -> str:
        """negative가 없을 때 시드에서 anchor와 다른 단어를 fallback으로 사용."""
        for a, p, n in SEED_TRIPLETS:
            if a != anchor and p != anchor:
                return n
        return "Cancel"

    # ------------------------------------------------------------------
    # Step 2: 통계 출력
    # ------------------------------------------------------------------

    @staticmethod
    def _print_stats(seed: list, collected: list):
        total = len(seed) + len(collected)
        print(f"\n📊 학습 데이터 현황")
        print(f"   시드 데이터     : {len(seed):>4}개")
        print(f"   수집 데이터     : {len(collected):>4}개  ← healer 실전 수집분")
        print(f"   ─────────────────────")
        print(f"   총합            : {total:>4}개")

    # ------------------------------------------------------------------
    # Step 3: Fine-tuning
    # ------------------------------------------------------------------

    def _finetune(self, examples: list[InputExample]) -> str:
        """TripletLoss로 Fine-tuning 실행."""
        print(f"\n⏳ 모델 로딩 중... ({self.base_model})")
        model = SentenceTransformer(self.base_model)

        # DataLoader
        loader = DataLoader(examples, shuffle=True, batch_size=self.batch_size)

        # TripletLoss — distance_metric 기본값: COSINE
        loss = losses.TripletLoss(model=model)

        warmup_steps = math.ceil(len(loader) * self.epochs * self.warmup_ratio)

        # 저장 경로에 타임스탬프 포함
        ts         = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(self.output_dir / f"v_{ts}")

        print(f"\n🚀 Fine-tuning 시작")
        print(f"   epochs      : {self.epochs}")
        print(f"   batch_size  : {self.batch_size}")
        print(f"   warmup_steps: {warmup_steps}")
        print(f"   학습 샘플   : {len(examples)}개")
        print(f"   저장 경로   : {output_path}\n")

        model.fit(
            train_objectives=[(loader, loss)],
            epochs=self.epochs,
            warmup_steps=warmup_steps,
            output_path=output_path,
            show_progress_bar=True,
            save_best_model=True,
        )

        return output_path

    # ------------------------------------------------------------------
    # Step 4: 검증
    # ------------------------------------------------------------------

    def _validate(self, model_path: str):
        """
        학습된 모델로 핵심 케이스 유사도 검증.
        Fine-tuning 전후 점수를 비교하여 개선 여부 확인.
        """
        print("\n📋 Fine-tuning 검증")
        print("-" * 50)

        model_before = SentenceTransformer(self.base_model)
        model_after  = SentenceTransformer(model_path)

        # 검증할 핵심 케이스: (설명, anchor, should_be_close, should_be_far)
        test_cases = [
            ("한→영 저장",    "저장",    "Save",       "취소"),
            ("유의어 작성→등록","작성",   "등록",       "삭제"),
            ("대소문자",      "create",  "Create",     "Delete"),
            ("혼동 방지",     "삭제",    "Remove",     "취소"),  # 취소가 멀어야 함
            ("내비게이션",    "Dashboard","Home",      "Settings"),
        ]

        all_passed = True

        for desc, anchor, close, far in test_cases:
            score_before_close = self._cos_sim(model_before, anchor, close)
            score_before_far   = self._cos_sim(model_before, anchor, far)
            score_after_close  = self._cos_sim(model_after,  anchor, close)
            score_after_far    = self._cos_sim(model_after,  anchor, far)

            # 기준: close > far (margin 0.05 이상이면 통과)
            passed = (score_after_close - score_after_far) > 0.05
            status = "✅" if passed else "⚠️ "
            if not passed:
                all_passed = False

            print(
                f"  {status} [{desc}] '{anchor}' ↔ '{close}' vs '{far}'\n"
                f"       before: {score_before_close:.3f} vs {score_before_far:.3f}  "
                f"→  after: {score_after_close:.3f} vs {score_after_far:.3f}"
            )

        print("-" * 50)
        if all_passed:
            print("  🎉 모든 검증 통과 — 모델 교체를 권장합니다.")
        else:
            print("  ⚠️  일부 케이스 미통과 — 데이터 보강 후 재학습을 권장합니다.")

    @staticmethod
    def _cos_sim(model: SentenceTransformer, a: str, b: str) -> float:
        from sentence_transformers import util
        ea = model.encode(a, convert_to_tensor=True)
        eb = model.encode(b, convert_to_tensor=True)
        return float(util.cos_sim(ea, eb)[0][0])


# ──────────────────────────────────────────────────────────────────────────────
# 모델 교체 헬퍼
# ──────────────────────────────────────────────────────────────────────────────

def replace_model(new_model_path: str):
    """
    Fine-tuning된 모델로 NLPEngine 싱글톤을 교체합니다.
    테스트 세션 시작 시 conftest.py에서 호출하거나 수동으로 실행합니다.

    사용 예시:
        from utils.finetune import replace_model
        replace_model("models/nlp_finetuned/v_20250302_120000")
    """
    from utils.nlp import NLPEngine
    NLPEngine.reset()
    engine = NLPEngine.get_instance(model_name=new_model_path)
    print(f"✅ NLPEngine 교체 완료: {new_model_path}")
    return engine


# ──────────────────────────────────────────────────────────────────────────────
# CLI 진입점
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Triplet Fine-tuning 파이프라인")
    parser.add_argument("--dry-run",   action="store_true", help="데이터 통계만 확인")
    parser.add_argument("--seed-only", action="store_true", help="시드 데이터만으로 학습")
    parser.add_argument("--epochs",    type=int, default=10, help="학습 epoch 수")
    parser.add_argument("--batch",     type=int, default=16, help="배치 크기")
    parser.add_argument("--model",     type=str,
                        default="jhgan/ko-sroberta-multitask", help="베이스 모델")
    args = parser.parse_args()

    tuner = TripletFineTuner(
        base_model=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
    )
    tuner.run(dry_run=args.dry_run, seed_only=args.seed_only)