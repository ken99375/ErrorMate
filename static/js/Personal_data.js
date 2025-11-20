// Personal.data.js

document.addEventListener('DOMContentLoaded', function() {
    // APIのURL（Python側で設定したURLに合わせる）
    const apiUrl = '/personal/LanguageRatio/data'; 

    const canvas = document.getElementById('languageChart');
    if (!canvas) return; // グラフ用キャンバスがないページでは実行しない

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(chartData => {
            
            // ★ここが修正ポイント：データがない場合の判定
            if (!chartData.labels || chartData.labels.length === 0) {
                // データが空ならエラーページへ飛ばす
                window.location.href = "/personal/DataError";
                return;
            }

            // データがある場合のみグラフを描画
            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        data: chartData.values,
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', 
                            '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' },
                        title: { display: true, text: '使用しているタグの割合' }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error:', error);
            // 通信エラー時もエラーページに飛ばすならコメントアウトを外す
            // window.location.href = "/personal/DataError";
        });
});