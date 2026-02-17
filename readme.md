.\venv\Scripts\Activate.ps1
가상환경 활성화

repomix .
repomix . -o repomix_packaging\repomix-output.xml
llm 패키징

python -m pytest tests/test_auth.py --headed --slowmo 500
