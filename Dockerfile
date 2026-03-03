FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

# 2. 상자 안에서 우리가 작업할 기준 폴더를 /app 으로 정합니다.
WORKDIR /app

# 3. 라이브러리 목록(requirements.txt)을 먼저 복사합니다.
COPY requirements.txt .

# 4. 파이썬 라이브러리들을 설치합니다. (캐시를 남기지 않아 용량을 아낍니다)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. 우리의 AI 테스트 코드와 모델(best.pt) 등 모든 파일을 상자 안으로 복사합니다.
COPY . .

# 6. 상자가 켜지면 기본으로 대기할 명령어 (실제 실행은 깃허브 액션에서 덮어씁니다)
CMD ["/bin/bash"]
