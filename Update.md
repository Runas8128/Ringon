# 2차 링곤이 대규모 업데이트

## 추가된 기능
* 공지에 에블핑을 쓰는 기능 사용 전에 확인하는 기능 추가
* 봇으로 DM시 첨부파일도 같이 보내는 기능 추가

## 수정된 기능
* 공지, 서버 배너/로고 수정 예약 기능 다른 파일로 분리
* 버그리포트를 상세하게 주도록 변경
* 덱리스트 관련 백엔드 기능을 클래스메서드 기반으로 변경
* 봇이 켜지기 전 메시지를 fetching하지 못하는 버그 수정
* 테스팅 채널 ID로 수정
* 메시지 fetching 실패 여부를 try-except-else문으로 체크

## 삭제된 기능
* 감지할 단어 추가 및 삭제 명령어 (직접 추가하는 방식으로 수정)
* 메시지 갯수 저장 기능
* 랜덤으로 핑하는 기능
* 인원점검 시작 기능 (일시적 제한)