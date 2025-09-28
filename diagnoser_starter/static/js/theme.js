// テーマ切替：クリック → <html data-theme="..."> を更新して localStorage に保存
(function () {
  function setTheme(name) {
    document.documentElement.setAttribute("data-theme", name);
    try { localStorage.setItem("app_theme", name); } catch(e) {}
  }

  // 初期化（保存済みがあれば適用）
  try {
    var saved = localStorage.getItem("app_theme");
    if (saved) setTheme(saved);
  } catch(e) {}

  // クリックイベント
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest(".theme-dot");
    if (!el) return;
    var name = el.getAttribute("data-theme");
    if (!name) return;
    setTheme(name);
  }, false);
})();
