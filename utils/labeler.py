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
            ".q-btn:not(header .q-btn)": 0,           
            "[role='button']:not(header [role='button'])": 0,  
            "button:not(header button)": 0,  
            
            # --- 1: 입력창 (Input) 💡 [수정됨] 드롭다운 안의 가짜 input 무시! ---
            "input:not(.q-select input)": 1,            
            "textarea": 1,         
            ".q-field__input:not(.q-select .q-field__input)": 1,  
            
            # --- 2: 링크/메뉴 (Link) ---
            "a": 2,                
            ".q-item": 2,          
            ".q-tab": 2,            

            # --- 3: 아바타 (Avatar) ---
            ".q-header .q-btn--round": 3,  
            ".q-header .q-avatar": 3,       

            # --- 4 : 드롭다운 (Select) ---
            ".q-select": 4,        
            "[role='combobox']": 4 
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