
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
    U6(("<div style='width:150px; height:60px; display:flex; justify-content:center; align-items:center; text-align:center;'>U4<br>프로젝트 delete 선택<br>입력</div>")):::user

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
    
    



