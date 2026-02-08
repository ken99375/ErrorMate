// static/js/personal/error_type_ratio.js

document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("errorTypePie");
  if (!canvas) return;

  if (typeof Chart === "undefined") {
    showError(canvas, "Chart.js が読み込まれていません");
    return;
  }

  const raw = window.ERROR_TYPE_RATIO_DATA;
  if (!raw || !raw.labels || !raw.datasets) {
    showError(canvas, "グラフデータが見つかりません（chart_data の受け渡しを確認）");
    return;
  }

  // 0件ばかりならメッセージ
  const total = (raw.datasets[0]?.data || []).reduce((a, b) => a + (Number(b) || 0), 0);
  if (total === 0) {
    showError(canvas, "エラーデータがありません（error_message があるカードが0件です）");
    return;
  }

  // 既に描画済みなら破棄
  if (window.__errorTypePieChart) {
    window.__errorTypePieChart.destroy();
  }

  window.__errorTypePieChart = new Chart(canvas, {
    type: "pie",
    data: raw,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
        tooltip: {
          enabled: true,
          callbacks: {
            label: (ctx) => {
              const label = ctx.label || "";
              const value = Number(ctx.raw || 0);
              const pct = ((value / total) * 100).toFixed(1);
              return `${label}: ${value}件 (${pct}%)`;
            }
          }
        }
      }
    }
  });
});

function showError(canvas, message) {
  const p = document.createElement("p");
  p.textContent = message;
  p.style.marginTop = "10px";
  p.style.opacity = "0.75";
  canvas.insertAdjacentElement("afterend", p);
}
