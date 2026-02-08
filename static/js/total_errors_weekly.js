document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("totalErrorsWeeklyChart");
  if (!canvas) return;

  const raw = window.TOTAL_ERRORS_WEEKLY_DATA ?? canvas.dataset.chart;
  if (!raw) return;

  let chartData;
  try {
    chartData = typeof raw === "string" ? JSON.parse(raw) : raw;
  } catch (e) {
    console.error("TOTAL_ERRORS_WEEKLY_DATA parse error:", e);
    return;
  }

  if (typeof Chart === "undefined") {
    console.error("Chart.js is not loaded.");
    return;
  }

  if (window.__totalErrorsWeeklyChart) {
    window.__totalErrorsWeeklyChart.destroy();
  }

  window.__totalErrorsWeeklyChart = new Chart(canvas, {
    type: "line",
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true },
        tooltip: { enabled: true }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0 }
        },
        x: {
          ticks: {
            autoSkip: false,
            maxRotation: 0,
            minRotation: 0
          }
        }
      }
    }
  });
});
