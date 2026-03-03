FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

# 1. 상자 안에서 우리가 작업할 기준 폴더를 /app 으로 정합니다.
WORKDIR /app

# 🌟 2. [용량 최적화] 무거운 GPU 대신 가벼운 CPU용 AI 엔진을 찌꺼기 없이 설치합니다.
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 3. 라이브러리 목록(requirements.txt)을 먼저 복사합니다.
COPY requirements.txt .

# 4. 파이썬 라이브러리들을 찌꺼기 없이 설치합니다.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 🌟 5. [속도 최적화] 테스트 도중에 다운로드하느라 멈추지 않도록, EasyOCR 모델을 상자 안에 미리 다운받아 둡니다!
RUN python -c "import easyocr; easyocr.Reader(['ko', 'en'])"

# 6. 우리의 AI 테스트 코드와 모델(best.pt) 등 모든 파일을 상자 안으로 복사합니다.
COPY . .

# 7. 상자가 켜지면 기본으로 대기할 명령어
CMD ["/bin/bash"]
