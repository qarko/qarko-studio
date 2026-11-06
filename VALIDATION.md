# Portfolio validation — 2026-11-06 UTC

구현 대상은 QARKO STUDIO와 CALM AI 두 정적 데모입니다. 실제 접수·결제·AI 처리·외부 연동은 없으며 검증도 그 계약에 맞췄습니다.

## 환경과 실행

Linux Debian 13, Node 24.22.1 / npm 11.9.0, Python Playwright 1.62.0. Chromium 151.0.7922.34 / WebKit 26.5를 실제 실행했습니다. WebKit 시스템 의존성의 사용자 공간 설치 방법과 ldconfig 사전 점검 차이는 [README](README.md)에 기록했습니다. 렌더 검사 자체를 생략하지 않았습니다.

고정된 npm lockfile 설치, Tailwind 4.3.4 CLI 빌드, html-validate 10.11.2, 두 JS 파일의 `node --check`, `tests/browser.py`, `tests/accessibility.py`, 상대 파일/anchor 검사 및 클라이언트 노출 패턴 검사를 수행합니다. TypeScript는 사용하지 않습니다.

## 실행 결과

최종 수정본으로 **64개 렌더 조합, 8개 상호작용 묶음, 4개 확대/모션 묶음, 4개 no-JS 묶음이 모두 통과**했습니다. npm ci, CSS build, HTML validation, JS syntax 검사도 통과했습니다. [`validation/browser-report.json`](validation/browser-report.json)에 실제 각 폭과 소스 SHA-256을, [`accessibility-report.json`](validation/accessibility-report.json)에 자동 접근성 결과를 남겼습니다. 원본 스크린샷은 로컬 `test-results/`에 있습니다.

## 검증 범위

- 두 페이지 × Chromium/WebKit × file://·로컬 HTTP × 320/375/390/430/768/1024/1440/1920 CSS px, 높이 900px.
- 문서 가로 넘침, 본문/제목/레이블/버튼 잘림 후보, 이미지 로드, h1 개수, 빈 anchor, 외부 요청 및 페이지 오류 검사.
- Chromium file://는 offline API를 적용했습니다. WebKit의 offline API+file:// 조합은 정상 로컬 파일에도 내부 오류가 나므로, 파일 실행 상태에서 외부 HTTP 요청을 차단했습니다. HTTP 모드는 두 엔진 모두 loopback 외 요청을 차단했습니다.
- 375px의 8개 엔진/프로토콜/페이지 조합에서 Enter로 시트 열기, 제목 초점, Tab 15회/Shift+Tab 8회 순환, Escape·명시적 닫기·트리거 초점 복귀·스크롤 잠금 해제를 확인합니다. 네이티브 close 이벤트는 비동기로 처리되어, 테스트는 잠금 해제 상태를 기다린 뒤 판정합니다.
- 빈 폼·잘못된 이메일·유효 입력 확인, 상태 메시지, SaaS 세 샘플 출력, 탭 클릭 및 방향키·Home/End, 네 FAQ 열기/닫기, 세 플랜의 폼 선택을 검증합니다. 네트워크 전송·저장소 기록이 없는 로컬 데모입니다.
- 모바일 독의 두 조작 대상은 44px 이상이며, Work anchor와 footer 하단 여백을 검사합니다. 시트는 safe-area·dvh·내부 스크롤로 구성했습니다.
- 각 엔진/페이지의 320px에서 글자 크기 200%와 reduced motion, JavaScript를 끈 375px 문서 읽기/FAQ/제출 비활성 상태를 확인합니다.
- 두 페이지의 375/768/1440px 스크린샷을 직접 검토합니다. 수정한 문제는 1024px CALM 장식 SVG의 가로 넘침, 모바일 비교표 caption의 세로 줄바꿈, 768px 견적 숫자의 불필요한 줄바꿈, WebKit의 밝은 native select 배경과 밝은 텍스트 충돌입니다. 마지막 항목은 native select를 유지하며 appearance·색상·화살표를 명시하고 실제 WebKit 캡처로 확인했습니다.

## 접근성·대비

axe-core 4.11.0의 WCAG 2 A/AA, 2.1 AA, 2.2 AA 규칙을 Chromium 375/1440px의 두 페이지에 실행했습니다. 자동 위반은 0건입니다. 색상 수동 검토 후보는 QARKO 7/6개, CALM 5/5개이며, 목업·회전/그래픽과 겹치는 텍스트 및 select의 CSS 화살표를 스크린샷으로 확인했습니다. 자동 위반 0이 전체 WCAG 적합성을 뜻하지 않습니다.

정적 색 쌍을 상대 휘도로 별도 계산했습니다. 본문/보조 본문 및 버튼의 최소 확인값은 5.16:1, 입력·검토 경계는 4.14:1, 테마 초점은 7.40:1입니다. 1px 장식 경계는 기능 식별용 경계와 분리했습니다. 전체 값은 `validation/contrast-report.json`에 있습니다.

## 한계

실제 iPhone/Android, 노치와 키보드, Safari 앱, Firefox, VoiceOver/TalkBack/NVDA 발화, 강제 색상 모드, 실제 브라우저 200/400% zoom, 모든 글꼴 실패 조합은 검증하지 않았습니다. 200%는 루트 글자 크기 스트레스이며 모바일 실기기 검증을 대체하지 않습니다. 실제 출시 환경의 LCP/INP/CLS·75백분위·저사양 성능은 측정하지 않았습니다. 반응형 100%·성능 점수·고객 성과를 주장하지 않습니다.

새 소스 커밋에 대한 Round 1 기록과 검토 요청만 구현했습니다. Peace의 감지·모니터링·5분 내 검수·승인 여부는 외부 실행 영역이며 확인하지 않았습니다.
