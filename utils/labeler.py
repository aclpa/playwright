import os
from datetime import datetime
from playwright.sync_api import Page

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
            "button:not(.q-header button), .q-btn:not(.q-header .q-btn), [role='button']:not(.q-header [role='button']), input[type='submit'], input[type='button']": 0,
            
            # --- 1: 입력창 (Input) ---
            "input:not([type='submit']):not([type='button']):not(.q-select input), textarea, .q-field__input:not(.q-select .q-field__input)": 1,
            
            # --- 2: 링크/메뉴 (Link) ---
            "a:not(.q-btn), .q-item, .q-tab": 2,

            # --- 3: 아바타 (Avatar) ---
            ".q-header .q-btn--round, .q-header .q-avatar": 3,

            # --- 4 : 드롭다운 (Select) ---
            ".q-select, [role='combobox']": 4 
        }

    # utils/labeler.py 수정
    def collect(self, page: Page, prefix: str = "page", target_locator=None):
        """
        target_locator가 주어지면 해당 부분만 캡처하고 기준 좌표를 재계산합니다.
        """
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000) 
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        img_name = f"{prefix}_{timestamp}.png"
        lbl_name = f"{prefix}_{timestamp}.txt"
        
        img_path = os.path.join(self.img_dir, img_name)
        lbl_path = os.path.join(self.lbl_dir, lbl_name)
        
        # 💡 [핵심] 전체 캡처 vs 부분 캡처 분기 처리
        if target_locator:
            parent_box = target_locator.bounding_box()
            vw, vh = parent_box['width'], parent_box['height']
            parent_x, parent_y = parent_box['x'], parent_box['y']
            target_locator.screenshot(path=img_path) # 부분만 캡처
        else:
            viewport = page.viewport_size
            vw, vh = viewport['width'], viewport['height']
            parent_x, parent_y = 0, 0
            page.screenshot(path=img_path) # 전체 캡처
        
        labels = []
        for selector, class_id in self.class_map.items():
            elements = page.locator(selector).all()
            for el in elements:
                if not el.is_visible():
                    continue
                
                box = el.bounding_box()
                if not box or box['width'] == 0 or box['height'] == 0:
                    continue
                    
                # 💡 [핵심] 부모 박스(부분 캡처 영역)를 기준으로 상대 좌표 계산
                rel_x = box['x'] - parent_x
                rel_y = box['y'] - parent_y
                
                # 객체가 캡처된 영역(부모 박스)을 완전히 벗어났다면 라벨링 제외
                if rel_x < 0 or rel_y < 0 or (rel_x + box['width']) > vw or (rel_y + box['height']) > vh:
                    continue
                    
                # 정규화 연산 (0.0 ~ 1.0)
                x_center = (rel_x + (box['width'] / 2)) / vw
                y_center = (rel_y + (box['height'] / 2)) / vh
                w_norm = box['width'] / vw
                h_norm = box['height'] / vh
                
                if 0 <= x_center <= 1 and 0 <= y_center <= 1:
                    labels.append(f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")
                    
        if labels:
            with open(lbl_path, "w", encoding="utf-8") as f:
                f.write("\n".join(labels))
            print(f"📸 [데이터 수집] {prefix} 화면 - 객체 {len(labels)}개 라벨링 완료!")
        else:
            os.remove(img_path)