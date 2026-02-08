document.addEventListener("DOMContentLoaded", () => {
  // canvasのidが違っても拾えるように候補を並べておく
  const canvas =
    document.getElementById("commentPostBar") ||
    document.getElementById("commentPostChart") ||
    document.getElementById("commentPostRankingChart");

  if (!canvas) return;

  // データ取得（グローバル変数 → data属性 の順）
  let raw = window.COMMENT_POST_RANKING_DATA ?? canvas.dataset.chart;

  if (!raw) {
    showError(canvas, "グラフデータが見つかりません（chart_data の受け渡しを確認してください）");
    return;
  }

  // JSON文字列ならパース
  let chartData;
  try {
    chartData = typeof raw === "string" ? JSON.parse(raw) : raw;
  } catch (e) {
    showError(canvas, "グラフデータの形式が不正です（JSONのパースに失敗しました）");
    console.error(e);
    return;
  }

  // Chart.js が読み込まれているか確認
  if (typeof Chart === "undefined") {
    showError(canvas, "Chart.js が読み込まれていません（CDN/scriptの読み込みを確認）");
    return;
  }

  // データがランキング配列形式でも対応（[{name,count}, ...] みたいな形）
  if (Array.isArray(chartData)) {
    chartData = {
      labels: chartData.map((x) => x.name ?? ""),
      datasets: [
          {
            label: "コメント送信数",
            data: chartData.map((x) => Number(x.count ?? 0)),
            backgroundColor: "rgba(255, 99, 132, 0.85)", // 赤（半透明）
            borderColor: "rgba(255, 99, 132, 1)",      // 赤（枠）
            borderWidth: 1,
          },
      ],
    };
  }

  // datasets が無い/空なら整える
  if (!chartData.datasets || !chartData.datasets.length) {
    chartData.datasets = [
      {
        label: "コメント送信数",
        data: [],
        backgroundColor: "rgba(120, 144, 156, 0.7)",
        borderColor: "rgba(0, 0, 0, 0.5)",
        borderWidth: 1,
      },
    ];
  } else {
    // 見た目が未指定ならデフォを入れる
    const ds0 = chartData.datasets[0];
    if (!ds0.backgroundColor) ds0.backgroundColor = "rgba(120, 144, 156, 0.7)";
    if (!ds0.borderColor) ds0.borderColor = "rgba(0, 0, 0, 0.5)";
    if (ds0.borderWidth == null) ds0.borderWidth = 1;
    if (!ds0.label) ds0.label = "コメント送信数";
  }

  // 既に描画済みなら破棄（ページ遷移なしで再描画するケース対策）
  if (window.__commentPostRankingChart) {
    window.__commentPostRankingChart.destroy();
  }

  window.__commentPostRankingChart = new Chart(canvas, {
    type: "bar",
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0, // 小数を出さない
          },
        },
        x: {
          ticks: {
            autoSkip: false, // 全員表示（多いと詰まるので必要ならtrueに）
            maxRotation: 0,
            minRotation: 0,
          },
        },
      },
    },
  });
});

function showError(canvas, message) {
  const p = document.createElement("p");
  p.textContent = message;
  p.style.marginTop = "10px";
  p.style.opacity = "0.75";
  p.style.fontSize = "0.95rem";
  canvas.insertAdjacentElement("afterend", p);
}