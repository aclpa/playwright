윈도우
.\venv\Scripts\Activate.ps1
맥
source .venv/bin/activate
가상환경 활성화

repomix .
repomix . -o repomix_packaging\repomix-output.xml
llm 패키징

python -m pytest tests/test_auth.py --headed --slowmo 500 -s

맥 환경설정
pip install -r requirements.txt
playwright install

변경된 요구사항에 맞춰 패키지 버전 업데이트
pip install -r requirements.txt

최신 YOLO 패키지 설치
pip install ultralytics
데이터 학습
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=30 imgsz=640 device=cpu exist_ok=True