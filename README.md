# Ringon 링곤이

Shadowverse Deck store/analyze bot, Ringon! Thanks you Thunderbull for helping with translating commands :)

섀도우버스 덱 저장/분석 봇, 링곤이입니다! 명령어 번역을 도와주신 천둥소님 감사드립니다 :)

## Key Features 주요 기능들

* Store n Manage Decks 덱의 저장 및 관리
* Provide Profiles for Users 유저별 프로필
* Schedule Changing Logo/Banner, and Writing Notices 로고/배너 변경 및 공지사항 작성 예약

## Upcoming contents 업데이트할 내용 목록

 - [x] Translate Commands 명령어 영문 번역
 - [ ] Translate Deck Names with Pre-defined values 미리 정의된 단어들을 기준으로 번역
 - [ ] More flexible translation system 더 유연한 번역 시스템

## Known Bugs 알려진 버그 목록

 - [x] Didn't storing decks and not showing Decks 덱 저장/검색이 안되는 버그
 - [x] Unnecessary charactors '<@!' in uploader mention 불필요한 문자 '<@!'가 업로더 멘션에 포함되는 버그
 - [x] Not sending bug report properly 버그 리포트를 제대로 받지 못하는 버그
 - [ ] Slash commands are not posted properly 슬래시 커맨드가 정상 추가되지 않는 버그

## Quick Example 예시

```
!search sword rt -> search rotation deck with sword class
!덱검색 로얄 로테 -> 로얄 클래스의 로테이션 덱 검색
```

### Help Command 도움말 명령어

!help -> Show All commands by group

!help help -> Show what you can do with `!help` command

`!도움말` / `!명령어` -> 모든 커맨드를 그룹별로 정렬

!도움말 명령어 -> `!도움말` 명령어로 할 수 있는 기능 정리 (`!도움말 도움말`의 경우 "도움말" 카테고리를 보여줌)
