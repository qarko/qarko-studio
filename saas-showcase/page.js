(() => {
  const samples = {
    launch: {
      text: "#제품팀 · 예시 메시지\n새 대시보드 공개 전에 모바일 차트 확인이 필요해요. 디자인팀은 빈 화면 문구를 검토해 주세요. 변경 내역은 출시 노트에 모아 주세요.",
      summary: "대시보드 출시 전 품질을 점검하고 변경 사항을 문서화합니다.",
      owner: "제품팀",
      tasks: [
        "모바일 차트 레이아웃 확인",
        "빈 화면 안내 문구 검토",
        "출시 노트에 변경 내역 정리",
      ],
      source: "#제품팀 메시지 1건",
    },
    feedback: {
      text: "#고객지원 · 예시 피드백\n내보내기 버튼을 찾기 어렵다는 의견이 있어요. 큰 파일은 완료 여부를 알기 어렵다고 해요. 다음 제품 회의에서 우선순위를 정해 주세요.",
      summary: "내보내기 기능의 발견성과 처리 상태 안내를 개선할지 검토합니다.",
      owner: "고객지원·제품팀",
      tasks: [
        "내보내기 버튼 위치 검토",
        "큰 파일의 진행 상태 안내 확인",
        "제품 회의에서 개선 우선순위 결정",
      ],
      source: "#고객지원 피드백 1건",
    },
    meeting: {
      text: "#주간회의 · 예시 메모\n이번 주에는 온보딩 문서를 정리합니다. 운영팀이 초안을 쓰고 디자인팀이 화면 캡처를 추가해요. 금요일에 함께 확인합시다.",
      summary: "온보딩 문서 초안을 만들고 팀 검토를 준비합니다.",
      owner: "운영팀",
      tasks: [
        "온보딩 문서 초안 작성",
        "설명용 화면 캡처 추가",
        "금요일 공동 검토 준비",
      ],
      source: "#주간회의 메모 1건",
    },
  };
  const select = document.querySelector("#sample-select");
  const organize = document.querySelector("#organize");
  organize.disabled = false;
  document.querySelector("#sample-text").textContent = samples[select.value].text;
  select.addEventListener("change", () => {
    document.querySelector("#sample-text").textContent =
      samples[select.value].text;
    document.querySelector("#preview-status").textContent =
      "새 샘플을 선택했습니다. 정리해 보기를 눌러 결과를 확인하세요.";
  });
  organize.addEventListener("click", () => {
    const sample = samples[select.value];
    document.querySelector(".output-summary").textContent = sample.summary;
    document.querySelector(".owner-label").textContent =
      `담당 제안 · ${sample.owner} (확인 필요)`;
    const list = document.querySelector(".output-checklist");
    list.replaceChildren(
      ...sample.tasks.map((task) => {
        const item = document.createElement("li");
        item.textContent = task;
        return item;
      }),
    );
    document.querySelector(".source-label").textContent =
      `출처 · 샘플 ${sample.source}`;
    document.querySelector("#preview-status").textContent =
      "샘플 정리 완료. 실제 AI 결과가 아닌 미리 작성된 예시입니다.";
  });
  const tabs = [...document.querySelectorAll("[data-tab]")];
  const panels = [...document.querySelectorAll("[data-panel]")];
  const tablist = document.querySelector(".feature-tabs");
  tablist.setAttribute("role", "tablist");
  tablist.setAttribute("aria-label", "기능 단계");
  tablist.setAttribute("aria-orientation", "vertical");
  function activate(index, focus = false) {
    tabs.forEach((tab, position) => {
      const selected = position === index;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      panels[position].hidden = !selected;
    });
    if (focus) tabs[index].focus();
  }
  tabs.forEach((tab, index) => {
    tab.disabled = false;
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-controls", panels[index].id);
    panels[index].setAttribute("role", "tabpanel");
    panels[index].tabIndex = 0;
    tab.addEventListener("click", () => activate(index));
    tab.addEventListener("keydown", (event) => {
      const directions = {
        ArrowRight: 1,
        ArrowDown: 1,
        ArrowLeft: -1,
        ArrowUp: -1,
      };
      let next;
      if (event.key in directions)
        next = (index + directions[event.key] + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next !== undefined) {
        event.preventDefault();
        activate(next, true);
      }
    });
  });
  activate(0);
  document.querySelectorAll("[data-plan]").forEach((link) =>
    link.addEventListener("click", () => {
      document.querySelector("#contact-plan").value = link.dataset.plan;
      document.querySelector('#contact [role="status"]').textContent =
        `${link.textContent.split(" ")[0]} 플랜을 선택했습니다. 내용을 입력해 주세요.`;
    }),
  );
})();
