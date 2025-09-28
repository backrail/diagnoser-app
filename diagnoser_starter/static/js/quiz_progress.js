(function () {
  const wrap = document.getElementById("progress-wrap");
  if (!wrap) return;

  const total = Number(wrap.dataset.total || 0);
  const fill = wrap.querySelector(".progress-fill");
  const text = wrap.querySelector(".progress-text");

  // 質問セクション単位で「少なくとも1つ選ばれているか」を数える
  function countAnswered() {
    const sections = document.querySelectorAll('[data-question]');
    let answered = 0;
    sections.forEach(sec => {
      // そのセクション内の input でチェックされているものが1つでもあるか？
      const checked = sec.querySelector('input[type="radio"]:checked, input[type="checkbox"]:checked');
      if (checked) answered += 1;
    });
    return answered;
  }

  function updateProgress() {
    const answered = countAnswered();
    const pct = total > 0 ? Math.round((answered / total) * 100) : 0;
    if (fill) fill.style.width = pct + "%";
    if (text) text.textContent = `${answered} / ${total}`;
  }

  // 入力の変化を監視
  document.addEventListener('change', (e) => {
    const t = e.target;
    if (t && (t.matches('input[type="radio"]') || t.matches('input[type="checkbox"]'))) {
      updateProgress();
    }
  });

  // 初期描画
  updateProgress();
})();
