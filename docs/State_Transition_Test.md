명세

테스트 항목 칸반보드 상태전이 테스팅 test_kanban.py

테스트 베이시스

칸반보드엔 To Do, In Progress, In Review, Testing, Done, Close 칼럼이 존재하고 등록한 이슈가 카드로 존재한다.

이슈는 생성시 항상 To Do 칼럼에서 시작한다.

드래그 엔 드롭 기능으로 To Do -> In Progress -> In Review -> Testing -> Done -> Close로 이동 가능하지만 역순,단계 건너뛰기는 안된다.

칼럼을 옮길때마다 카드의 상태는 칼럼명과 동일하게 변경된다.

