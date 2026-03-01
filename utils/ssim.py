import cv2
from skimage.metrics import structural_similarity as ssim
import os

class SSIMChecker:
    @staticmethod
    def check_layout(baseline_path: str, current_path: str, diff_save_path: str = "diff_result.png") -> float:
        """
        두 이미지를 비교하여 구조적 유사도(SSIM) 점수를 반환합니다.
        기준 이미지(baseline)가 없으면 현재 이미지를 기준으로 저장하고 100점을 반환합니다.
        """
        # 1. 기준 이미지(Baseline) 자동 생성 로직
        if not os.path.exists(baseline_path):
            print(f"📸 기준 이미지(Baseline)가 없어 새로 생성합니다: {baseline_path}")
            current_img = cv2.imread(current_path)
            cv2.imwrite(baseline_path, current_img)
            return 100.0

        # 2. 이미지 읽기 및 흑백 변환 (구조 비교를 위해)
        imgA = cv2.imread(baseline_path)
        imgB = cv2.imread(current_path)
        
        # 이미지 크기가 다르면 에러 발생 방지를 위해 current 이미지를 baseline 크기에 맞춤
        if imgA.shape != imgB.shape:
            imgB = cv2.resize(imgB, (imgA.shape[1], imgA.shape[0]))

        grayA = cv2.cvtColor(imgA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imgB, cv2.COLOR_BGR2GRAY)

        # 3. SSIM 유사도 계산 (score: -1.0 ~ 1.0)
        score, diff = ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")
        
        similarity = score * 100

        # 4. 차이가 발생했을 때 (예: 98점 미만) 빨간색 네모 쳐서 저장하기
        print(f"📊 SSIM 레이아웃 검증 결과: {similarity:.2f}% -> {diff_save_path} 에 차이점 결과 저장됨")
        
        # 차이점(diff)을 이진화(흑백) 처리해서 윤곽선 찾기
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        img_diff = imgB.copy() # 현재 스크린샷 복사
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # 너무 자잘한 픽셀 차이는 무시 (노이즈 필터링)
            if w > 5 and h > 5: 
                # 차이가 나는 부분에 빨간색(0, 0, 255) 네모 그리기
                cv2.rectangle(img_diff, (x, y), (x + w, y + h), (0, 0, 255), 2) 
        
        # 무조건 저장
        cv2.imwrite(diff_save_path, img_diff)

        return similarity