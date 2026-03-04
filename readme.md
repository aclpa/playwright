
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
해결한 점
해결 못한 문제
개발 방법

## 📁 파일 구조
```
📦 프로젝트 루트
├── 📄 data.yaml                  # YOLO 학습 데이터셋 설정 (9개 클래스)
├── 📄 Dockerfile                 # Docker 이미지 빌드 (CPU 최적화)
├── 📄 pytest.ini                 # pytest 실행 설정
├── 📄 requirements.txt           # Python 패키지 목록
│
├── 📁 .github/workflows/
│   └── e2e-test.yml              # GitHub Actions CI/CD 파이프라인
│
├── 📁 pages/                     # Page Object Model (POM)
│   ├── base_page.py              # 공통 기반 — AIHealer click/fill 연결
│   ├── dashboard_page.py         # 대시보드 (유저 메뉴, 로그아웃)
│   ├── issue_page.py             # 이슈 생성
│   ├── kanban_page.py            # 칸반 드래그 앤 드롭
│   ├── login_page.py             # 로그인 / API 토큰 인증
│   ├── profile_page.py           # 프로필 수정
│   ├── project_page.py           # 프로젝트 생성
│   ├── sprint_page.py            # 스프린트 생성
│   └── team_page.py              # 팀 생성
│
├── 📁 tests/
│   ├── conftest.py               # 공용 픽스처 (브라우저 설정, API 인증 컨텍스트)
│   ├── data_collect.py           # YOLO 학습용 라벨 데이터 자동 수집
│   └── 📁 playwright/
│       ├── test_auth.py          # TC1~3: 로그인 성공 / API 로그인 / 로그아웃
│       ├── test_issue.py         # TC4: 이슈 생성
│       ├── test_kanban.py        # TC5: 칸반 드래그 앤 드롭
│       ├── test_profile.py       # TC6: 프로필 수정
│       ├── test_project.py       # TC7: 프로젝트 생성
│       ├── test_sprint.py        # TC8: 스프린트 생성
│       └── test_team.py          # TC9: 팀 생성
│
├── 📁 utils/                     # AI 핵심 엔진
│   ├── best.onnx                 # 학습된 YOLO 모델 (CPU 최적화 ONNX 포맷)
│   ├── yolo.py                   # YOLOEngine 싱글톤 — UI 객체 탐지
│   ├── nlp.py                    # NLPEngine 싱글톤 — 의미 유사도 추론
│   ├── healer.py                 # AIHealer — 자가 복구 메인 로직
│   └── labeler.py                # AutoLabeler — 학습 데이터 자동 라벨링
│
├── 📁 media/                     # 스크린샷 및 디버그 이미지 샘플
└── 📁 testim/healing/            # 자가 복구 시 자동 생성되는 힐링 이미지
```

### TC 프로젝트 생성 기능의 이벤트 흐름 다이어그램
```mermaid
%%{init: {"flowchart": {"curve": "stepBefore"}}}%%
flowchart LR

    classDef user fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef system fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef error fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    classDef success fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    
    Start([테스트 시작])
    End([테스트 종료])


    U1(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U1<br>아이디/비밀번호<br>입력</div>")):::user
    U2(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U2<br>Projects<br>카테고리 클릭</div>")):::user
    U3(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U3<br>NEW PROJECT<br>버튼 클릭</div>")):::user
    U4(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U4<br>프로젝트 필드칸<br>입력</div>")):::user
    U5(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U5<br>프로젝트 선택<br>입력</div>")):::user
    U6(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U6<br>프로젝트 delete 선택</div>")):::user

    S1.1["S1.1 시스템 로그인 수락"]:::system 
    S1.2["S1.2 시스템 로그인 거부"]:::system
    S2.1["S2.1 시스템 프로젝트 생성"]:::system
    S2.2["S2.2 이름 입력 누락"]:::system
    S2.3["S2.3 키 입력 누락"]:::system 
    S2.4["S2.4 키 중복 에러"]:::system
    S2.5["S2.5 Team 선택 누락"]:::system
    S3["S3 프로젝트 삭제 /projects로 리디렉션"]:::system
    
    Start --> U1
    U1  ==> S1.1
    S1.1 ==> U2
    U2 ==> U3
    U3 ==> U4
    U4 ==> S2.1
    S2.1 ==> U5
    U5 ==> U6
    U6 ==> S3
    S3 ==> End
    
    U1 --> S1.2
    U4 <-- 에러/리턴 --> S2.2  
    U4 <-- 에러/리턴 --> S2.3  
    U4 <-- 에러/리턴 --> S2.4  
    U4 <-- 에러/리턴 --> S2.5  

     
    
    linkStyle 1,2,3,4,5,6,7,8,9 stroke-width:4px,stroke:blue;
    linkStyle 10,11,12,13,14 stroke-width:4px,stroke:red;
```



