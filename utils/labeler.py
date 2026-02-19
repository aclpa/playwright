# utils/labeler.py
import os
from datetime import datetime
from matplotlib.dviread import Page

class AutoLabeler:
    def __init__(self, base_dir="datasets"):
        # YOLOv8 학습용 폴더 구조 자동 생성
        self.img_dir = os.path.join(base_dir, "images", "train")
        self.lbl_dir = os.path.join(base_dir, "labels", "train")
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.lbl_dir, exist_ok=True)
        
        # AI가 인식할 클래스 ID 매핑 (0: 버튼, 1: 입력창, 2: 링크)
        self.class_map = {
            # --- 0: 버튼 (Button) ---
            "button": 0,           # 기본 HTML 버튼
            ".q-btn": 0,           # Quasar 버튼 (상단 햄버거 메뉴, 돋보기, 파란 버튼 등)
            "[role='button']": 0,  # 버튼 역할을 하는 기타 요소
            
            # --- 1: 입력창 (Input) ---
            "input": 1,            # 기본 HTML 입력창
            "textarea": 1,         # 여러 줄 입력창
            ".q-field__input": 1,  # Quasar 입력창
            
            # --- 2: 링크/메뉴 (Link) ---
            "a": 2,                # 기본 HTML 링크
            ".q-item": 2,          # Quasar 사이드바 메뉴 항목들 (Projects, Sprints 등)
            ".q-tab": 2            # Quasar 탭 메뉴 (있는 경우 대비)
        }

    def collect(self, page: Page, prefix: str = "page"):
        """현재 화면의 스크린샷과 YOLO 라벨 텍스트를 생성합니다."""
        
        # 화면이 완전히 렌더링될 때까지 대기
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000) # 애니메이션 안정화 대기
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        img_name = f"{prefix}_{timestamp}.png"
        lbl_name = f"{prefix}_{timestamp}.txt"
        
        img_path = os.path.join(self.img_dir, img_name)
        lbl_path = os.path.join(self.lbl_dir, lbl_name)
        
        # 스크린샷 캡처
        page.screenshot(path=img_path)
        
        viewport = page.viewport_size
        vw, vh = viewport['width'], viewport['height']
        
        labels = []
        for selector, class_id in self.class_map.items():
            elements = page.locator(selector).all()
            for el in elements:
                if not el.is_visible():
                    continue
                
                box = el.bounding_box()
                if not box or box['width'] == 0 or box['height'] == 0:
                    continue
                    
                # 💡 [핵심] 정규화 (Normalization) 연산
                x_center = (box['x'] + (box['width'] / 2)) / vw
                y_center = (box['y'] + (box['height'] / 2)) / vh
                w_norm = box['width'] / vw
                h_norm = box['height'] / vh
                
                # 뷰포트 안에 있는 정상적인 요소만 기록
                if 0 <= x_center <= 1 and 0 <= y_center <= 1:
                    labels.append(f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")
                    
        # 파일 저장 로직
        if labels:
            with open(lbl_path, "w", encoding="utf-8") as f:
                f.write("\n".join(labels))
            print(f"📸 [데이터 수집] {prefix} 화면 - 객체 {len(labels)}개 라벨링 완료!")
        else:
            # 라벨링할 객체가 하나도 없으면 스크린샷 파일 삭제
            os.remove(img_path)