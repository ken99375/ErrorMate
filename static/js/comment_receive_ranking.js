document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("commentReceiveBar");
  if (!canvas) return;

  if (typeof Chart === "undefined") {
    console.error("Chart.js が読み込まれていません（script順を確認）");
    return;
  }

  const dataTag = document.getElementById("chart-data");
  if (!dataTag) {
    console.error("chart-data が見つかりません");
    return;
  }

  let chartData;
  try {
    chartData = JSON.parse(dataTag.textContent);
  } catch (e) {
    console.error("chart_data のJSONパースに失敗:", e);
    console.log("raw:", dataTag.textContent);
    return;
  }

  // ★棒を青にする
  if (chartData.datasets && chartData.datasets[0]) {
    chartData.datasets[0].backgroundColor = "rgba(33, 150, 243, 0.75)"; // 青
    chartData.datasets[0].borderColor = "rgba(13, 71, 161, 1.0)";
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
