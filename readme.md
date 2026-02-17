윈도우
.\venv\Scripts\Activate.ps1
맥
source venv/bin/activate
가상환경 활성화

repomix .
repomix . -o repomix_packaging\repomix-output.xml
llm 패키징

python -m pytest tests/test_auth.py --headed --slowmo 500

# 1. develop 브랜치로 이동 및 최신화
git checkout develop
git pull origin develop

# 2. 기능 브랜치 생성 (예: feature/tc4-payment)
git checkout -b feature/[기능명]

# 3. 코드 작업 후 커밋
git add .
git commit -m "Add [기능명] test case"

# 4. 완료 후 develop에 합치기 (Recursive Merge)
git checkout develop
git merge --no-ff feature/[기능명] -m "Merge [기능명] into develop"

# 5. 원격 저장소 업로드 및 브랜치 삭제
git push origin develop
git branch -d feature/[기능명]
# 1. 릴리즈 브랜치 생성 (버전은 v1.2.0 등으로 올림)
git checkout develop
git checkout -b release/[버전명]

# 2. (선택) readme.md 수정 등 최종 점검 후 커밋
git add .
git commit -m "Update version [버전명]"

# 3. main 브랜치에 합치고 태그 달기
git checkout main
git merge --no-ff release/[버전명] -m "Release [버전명]: 배포 요약"
git tag -a [버전명] -m "Release version [버전명]"

# 4. 수정사항을 다시 develop에도 반영
git checkout develop
git merge --no-ff release/[버전명]

# 5. 최종 푸시 및 브랜치 삭제
git push origin main --tags
git push origin develop
git branch -d release/[버전명]

명령어 옵션: merge 할 때 --no-ff를 꼭 붙여주세요. 그래야 나중에 어떤 기능이 추가되었는지 히스토리가 선명하게 남습니다

맥 환경설정
pip install -r requirements.txt
playwright install
