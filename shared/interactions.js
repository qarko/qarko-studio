(() => {
  const dialog = document.querySelector("dialog");
  let trigger;
  document.querySelectorAll("[data-open-inquiry]").forEach((button) => {
    button.disabled = false;
    button.addEventListener("click", () => {
      trigger = button;
      dialog.showModal();
      document.body.classList.add("modal-open");
      dialog.querySelector("h2").focus();
    });
  });
  if (dialog) {
    dialog
      .querySelector("[data-close]")
      .addEventListener("click", () => dialog.close());
    dialog.addEventListener("close", () => {
      document.body.classList.remove("modal-open");
      trigger?.focus();
    });
    dialog.addEventListener("keydown", (event) => {
      if (event.key !== "Tab") return;
      const controls = [
        ...dialog.querySelectorAll(
          "button:not(:disabled), input, textarea, select, a[href]",
        ),
      ];
      const first = controls[0];
      const last = controls.at(-1);
      if (
        event.shiftKey &&
        (document.activeElement === first ||
          document.activeElement === dialog.querySelector("h2"))
      ) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }
  document.querySelectorAll("[data-local-form]").forEach((form) => {
    const submit = form.querySelector("[data-submit]");
    submit.disabled = false;
    const error = form.querySelector("[data-error]");
    const status = form.querySelector('[role="status"]');
    form.addEventListener(
      "invalid",
      () => {
        error.textContent = "필수 항목과 이메일 형식을 확인해 주세요.";
      },
      true,
    );
    form.addEventListener("input", () => {
      error.textContent = "";
      status.textContent = "";
    });
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      error.textContent = "";
      const plan = form.querySelector('[name="plan"]');
      status.textContent = `문의 내용을 확인했습니다${plan ? " · " + plan.selectedOptions[0].textContent : ""}. 이 데모는 전송하거나 저장하지 않습니다.`;
    });
  });
})();
