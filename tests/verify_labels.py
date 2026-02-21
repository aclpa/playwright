import cv2
import os
import glob

def verify_yolo_labels(base_dir="datasets", sample_count=5):
    img_dir = os.path.join(base_dir, "images", "train")
    lbl_dir = os.path.join(base_dir, "labels", "train")
    output_dir = os.path.join(base_dir, "verify_output")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 이미지 파일 목록 가져오기 (.png 기준)
    image_paths = glob.glob(os.path.join(img_dir, "*.png"))
    
    if not image_paths:
        print("❌ 이미지를 찾을 수 없습니다. 경로를 확인해 주세요.")
        return

    print(f"총 {len(image_paths)}개의 이미지를 찾았습니다. {sample_count}개를 샘플링하여 검증합니다.\n")

    for img_path in image_paths[:sample_count]:
        # 파일명 추출 (확장자 제외)
        basename = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(lbl_dir, f"{basename}.txt")
        
        # 1. 이미지 읽기
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        h, w, _ = img.shape
        
        # 2. 라벨 파일이 존재하는지 확인
        if not os.path.exists(lbl_path):
            print(f"⚠️ [경고] {basename}.txt 라벨 파일이 없습니다.")
            continue
            
        # 3. 라벨 읽어서 박스 그리기
        with open(lbl_path, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
                
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            
            # YOLO 정규화 좌표(0~1)를 실제 픽셀 좌표로 복원
            x_min = int((x_center - width / 2) * w)
            y_min = int((y_center - height / 2) * h)
            x_max = int((x_center + width / 2) * w)
            y_max = int((y_center + height / 2) * h)
            
            # 빨간색 박스 그리기 (BGR 기준: 0, 0, 255)
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
            
            # 클래스 ID 텍스트 적기
            cv2.putText(img, f"Class: {class_id}", (x_min, y_min - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # 4. 결과 저장
        out_path = os.path.join(output_dir, f"verified_{basename}.png")
        cv2.imwrite(out_path, img)
        print(f"✅ 검증 완료: {out_path} (라벨 {len(lines)}개)")

if __name__ == "__main__":
    verify_yolo_labels()