윈도우
.\venv\Scripts\Activate.ps1
맥
source .venv/bin/activate
가상환경 활성화

repomix .
repomix . -o repomix_packaging\repomix-output.xml
llm 패키징

python3 -m pytest tests/test_auth.py --headed --slowmo 500 -s


환경설정
pip3 install -r requirements.txt

최신 YOLO 패키지 설치
pip install ultralytics
데이터 학습
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100 imgsz=1024 device=0 batch=4 workers=0 exist_ok=True