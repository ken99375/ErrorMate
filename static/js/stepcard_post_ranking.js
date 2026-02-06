document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("stepcardBar");
  if (!canvas) return;

  // Chart.js 読み込み確認
  if (typeof Chart === "undefined") {
    console.error("Chart.js が読み込まれていません（CDNのscriptタグ順を確認）");
    return;
  }

  // JSONデータをHTMLから読む
  const dataTag = document.getElementById("chart-data");
  if (!dataTag) {
    console.error("chart-data が見つかりません");
    return;
  }

  let chartData;
  try {
    chartData = JSON.parse(dataTag.textContent);
  } catch (e) {
    console.error("chart_data のJSONパースに失敗しました:", e);
    console.log("raw:", dataTag.textContent);
    return;
  }
  
      // 棒を黄色にする
  if (chartData.datasets && chartData.datasets[0]) {
      chartData.datasets[0].backgroundColor = "rgba(255, 235, 59, 0.8)"; 
      chartData.datasets[0].borderColor = "rgba(255, 193, 7, 1.0)";      
      chartData.datasets[0].borderWidth = 1;
  }

  new Chart(canvas, {
    type: "bar",
    data: chartData,
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true },
        x: { ticks: { maxRotation: 0, minRotation: 0, autoSkip: false } }
      }
    }
  });
});
