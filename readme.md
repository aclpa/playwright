
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
ISO 29119-4
자동화를 도입한 배경
개선한 내용

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
명세
ERP 일부 기능인 프로젝트 생성 이라는 테스트 항목이 있고 테스트 베이시스는 다음과 같다.
프로젝트 생성 기능은 사용자가 관리할 프로젝트를 생성하도록 해 준다. 프로젝트 생성은 
프로젝트 필드에서 프로젝트 생성 버튼을 누른 뒤 프로젝트 필드 칸을 채운다.프로젝트 필드로는 프로젝트 이름,프로젝트 키,프로젝트 설명, 상태,팀,시작-종료일,배포 URL을 설정할 수 있다.
프로젝트를 생성하면 DB에 저장되 등록된 팀은 프로젝트를 관리할 수 있다.

일반적 시나리오

-프로젝트 생성

대체 시나리오
-다음과 같은 이유로 프로젝트 생성에 실패함.

-프로젝트 이름 누락

-프로젝트 키 누락

-중복된 프로젝트 키

-프로젝트 키 소문자 입력

-프로젝트 키 숫자로 시작

-프로젝트 키 한글 입력

-프로젝트 키 특수문자 입력

-팀 선택 누락

비고 프로젝트 이름은 중복가능, 배포 URL 시작-종료일,프로젝트 설명은 누락가능하다.

스텝 1 :기능 세트 식별(TD1)

FS1 = 프로젝트 생성 기능

스텝 2 : 테스트 컨디션 도출(TD2)

다음 모델의 예는 이벤트 흐름 다이어그램이다. 이 표기법에서 성공 흐름은 파란색 선으로 표시되어 있고, 테스트 시작과 종료 시점이 명시되어 있으며, 각 액션은 고유 ID가 있어 사용자(U) 시스템(S)로 지정한다.

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

    U1(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U1<br>NEW PROJECT<br>버튼 클릭</div>")):::user
    U2(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U2<br>프로젝트 필드<br>입력</div>")):::user
    U3(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U3<br>명세된 필드<br>입력</div>")):::user
    U2.1(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U2.1<br>CANCEL<br>입력</div>")):::user

    S1.1["S1.1  프로젝트 필드 출력"]:::system
    S1.2["S1.2 이름 입력 누락"]:::system
    S1.3["S1.3 키 입력 누락"]:::system 
    S1.4["S1.4 키 중복 "]:::system
    S1.5["S1.5 키 소문자 입력 "]:::system
    S1.6["S1.6 키 숫자로 시작 "]:::system
    S1.7["S1.7 키 한글 입력"]:::system
    S1.8["S1.8 키 특수문자 입력"]:::system
    S1.9["S1.9 Team 선택 누락"]:::system
    S2["S2 프로젝트 생성"]:::system
    
    Start ==> U1
    U1  ==> S1.1
    S1.1 ==> U2
    U2 ==> U3
    U3 ===> S2 ==> End
 
    U2 <-- 에러/리턴 --> S1.2  <--에러/리턴-->S2
    U2 <-- 에러/리턴 --> S1.3  <--에러/리턴-->S2
    U2 <-- 에러/리턴 --> S1.4  
    U2 <-- 에러/리턴 --> S1.5
    U2 <-- 에러/리턴 --> S1.6
    U2 <-- 에러/리턴 --> S1.7
    U2 <-- 에러/리턴 --> S1.8   
    U2 <-- 에러/리턴 --> S1.9  <--에러/리턴-->S2

    U2 --실패-->U2.1 -->U1
     
    linkStyle 0,1,2,3,4,5 stroke-width:4px,stroke:blue;
    linkStyle 6,7,8,9,10,11,12,13,14,15,16,17,18 stroke-width:4px,stroke:red;

```
테스트 컨디션

TC COND1 : 프로젝트 생성 성공(U1,S1.1,U2,U3,S2)

TC COND2 : 프로젝트 이름 누락(U1,S1.1,U2,S1.2)

TC COND3 : 프로젝트 키 누락(U1,S1.1,U2,S1.3)

TC COND4 : 프로젝트 키 중복(U1,S1.1,U2,S1.4)

TC COND5 : 프로젝트 키 소문자 입력(U1,S1.1,U2,S1.5)

TC COND6 : 프로젝트 키 숫자로 시작(U1,S1.1,U2,S1.6)

TC COND7 : 프로젝트 키 한글 입력(U1,S1.1,U2,S1.7)

TC COND8 : 프로젝트 키 특수문자 입력(U1,S1.1,U2,S1.8)

TC COND9 : 팀 선택 누락(U1,S1.1,U2,S1.9)

TC COND10 : CANCEL 선택(U1,S1.1,U2,U2.1)


스텝 3 : 테스트 커버리지 항목 도출(TD3)

TC COVER1 = TC COND1

TC COVER2 = TC COND2

TC COVER3 = TC COND3

TC COVER4 = TC COND4

TC COVER5 = TC COND5

TC COVER6 = TC COND6

TC COVER7 = TC COND7

TC COVER8 = TC COND8

TC COVER9 = TC COND9

TC COVER10 = TC COND10

스텝 4 : 테스트 케이스 도출(TD4)

시나리오 테스팅 케이스

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 1 |
| **테스트 케이스 명** | 프로젝트 생성 성공 |
| **수행할 시나리오 경로** | U1, S1.1, U2, U3, S2 |
| **입력** | -NEW PROJECT 클릭<br>-프로젝트 필드 값 입력<br>-CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다. |
| **기대 결과** | -프로젝트 목록 페이지(#/projects)에 생성한 프로젝트 보임 <br>-생성된 프로젝트에 입력한 정보 일치 |
| **테스트 커버리지 항목** | TC COVER1 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 2 |
| **테스트 케이스 명** | 프로젝트 이름 누락 |
| **수행할 시나리오 경로** | U1, S1.1, U2, S1.2 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 키,Team 필드값은 입력 되어있다고 가정<br>-프로젝트 이름 * 필드값이 비어있는 상태로 CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다.<br>프로젝트 키는 중복된 값이 아니어야 한다. |
| **기대 결과** | -프로젝트 이름 필드가 선택되며 "프로젝트 이름은 필수입니다" 경고 메세지 출력  |
| **테스트 커버리지 항목** | TC COVER2 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 3 |
| **테스트 케이스 명** | 프로젝트 키 누락 |
| **수행할 시나리오 경로** | U1, S1.1, U2, S1.3 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 이름,Team 필드값은 입력 되어있다고 가정<br>-프로젝트 키 * 필드값이 비어있는 상태로 CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다. |
| **기대 결과** | -프로젝트 키 필드가 선택되며 "프로젝트 키는 필수입니다" 경고 메세지 출력  |
| **테스트 커버리지 항목** | TC COVER3 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 4 |
| **테스트 케이스 명** | 프로젝트 키 중복 |
| **수행할 시나리오 경로** | U1, S1.1, U2, S1.4 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 이름,Team 필드값은 입력 되어있다고 가정<br>-프로젝트 키 * 필드값에 "TEST"입력후 CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다.<br>사전에 "TEST" 키 값을 가지고 있는 프로젝트가 생성되어 있어야 한다. |
| **기대 결과** | -상단 중앙에 "Fauled to create project", 우측 상단에 잘못된 요청입니다 "Project with key 'TEST' already exists" 토스트 메세지 출력 |
| **테스트 커버리지 항목** | TC COVER4 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 5 |
| **테스트 케이스 명** | 프로젝트 키 소문자 입력 |
| **수행할 시나리오 경로** | U1, S1.1, U2, S1.5 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 이름,Team 필드값은 입력 되어있다고 가정<br>-프로젝트 키 * 필드값에 소문자 입력후 CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다.<br>프로젝트 키 필드 아래 "대문자로 시작, 대문자와 숫자만 가능 (예: PROJ1, DEV)"이 명시되어 있다. |
| **기대 결과** | -프로젝트 키 필드가 선택되며 "대문자로 시작하고 대문자와 숫자만 사용 가능합니다" 경고 메세지 출력  |
| **테스트 커버리지 항목** | TC COVER5 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 6 |
| **테스트 케이스 명** | 프로젝트 키 숫자로 시작 |
| **수행할 시나리오 경로** | U1, S1.1, U2, S1.6 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 이름,Team 필드값은 입력 되어있다고 가정<br>-프로젝트 키 * 필드값에 숫자 입력후 CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다.<br>프로젝트 키 필드 아래 "대문자로 시작, 대문자와 숫자만 가능 (예: PROJ1, DEV)"이 명시되어 있다. |
| **기대 결과** | -프로젝트 키 필드가 선택되며 "대문자로 시작하고 대문자와 숫자만 사용 가능합니다" 경고 메세지 출력  |
| **테스트 커버리지 항목** | TC COVER6 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 7 |
| **테스트 케이스 명** | 프로젝트 키 한글 입력 |
| **수행할 시나리오 경로** | U1, S1.1, U2, S1.7 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 이름,Team 필드값은 입력 되어있다고 가정<br>-프로젝트 키 * 필드값에 한글 입력후 CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다.<br>프로젝트 키 필드 아래 "대문자로 시작, 대문자와 숫자만 가능 (예: PROJ1, DEV)"이 명시되어 있다. |
| **기대 결과** | -프로젝트 키 필드가 선택되며 "대문자로 시작하고 대문자와 숫자만 사용 가능합니다" 경고 메세지 출력  |
| **테스트 커버리지 항목** | TC COVER7 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 8 |
| **테스트 케이스 명** | 프로젝트 키 특수문자 입력 |
| **수행할 시나리오 경로** | U1, S1.1, U2, S1.8 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 이름,Team 필드값은 입력 되어있다고 가정<br>-프로젝트 키 * 필드값에 특수문자 입력후 CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다.<br>프로젝트 키 필드 아래 "대문자로 시작, 대문자와 숫자만 가능 (예: PROJ1, DEV)"이 명시되어 있다. |
| **기대 결과** | -프로젝트 키 필드가 선택되며 "대문자로 시작하고 대문자와 숫자만 사용 가능합니다" 경고 메세지 출력  |
| **테스트 커버리지 항목** | TC COVER8 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 9 |
| **테스트 케이스 명** | 프로젝트 팀 선택 누락 |
| **수행할 시나리오 경로** | U1, S1.1, U2, S1.9 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 이름,프로젝트 키 필드값은 입력 되어있다고 가정<br>-Team * 필드  기본값 "0"인 상태로 CREATE 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다.<br>중복된 키 값을 가진 project가 없어야 한다. |
| **기대 결과** | -팀 필드 아래 "Team is required" 출력  |
| **테스트 커버리지 항목** | TC COVER9 |

| 항목 | 내용 |
| :--- | :--- |
| **테스트 케이스 #** | 10 |
| **테스트 케이스 명** | 프로젝트 CANCEL 선택 |
| **수행할 시나리오 경로** | U1, S1.1, U2, U2.1 |
| **입력** | -프로젝트 생성 필드가 열려있는 상태로 가정<br>-프로젝트 이름,프로젝트 키, 팀 필드값은 입력 되어있다고 가정<br>-CANCEL 클릭  |
| **사전 조건** | 유효한 사용자가 로그인한 상태여야 프로젝트 생성이 가능하다. |
| **기대 결과** | -생성 필드가 사라지며 프로젝트 목록 페이지로 리턴 (#/projects)  |
| **테스트 커버리지 항목** | TC COVER10 |