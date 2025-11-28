document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.like-btn');
  if (!btn) return;

  if (btn.dataset.auth !== '1') {
    /* global location*/
    location.href = btn.dataset.login || '/auth/login';
    return;
  }

  const cardId = btn.dataset.card;
  try {
      /* global fetch*/
    const res = await fetch(`/share/card/${cardId}/like`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'fetch' },
      credentials: 'same-origin'
    });
    if (!res.ok) throw new Error('bad response');
    const data = await res.json();

    btn.setAttribute('aria-pressed', data.liked ? 'true' : 'false');
    btn.querySelector('.heart').textContent = data.liked ? '♥' : '♡';
    btn.querySelector('.like-count').textContent = data.count;
  } catch (err) {
    console.error(err);
    alert('通信に失敗しました');
  }
});


document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.like-btn');
  if (!btn) return;

  // ログインしていない場合はログインページへ
  if (btn.dataset.auth !== '1') {
    location.href = btn.dataset.login || '/auth/login';
    return;
  }

  const cardId = btn.dataset.card;
  try {
    const res = await fetch(`/share/help/${cardId}/like`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'fetch' },
      credentials: 'same-origin'
    });

    if (!res.ok) throw new Error('bad response');
    const data = await res.json();

    // ボタン状態更新
    btn.setAttribute('aria-pressed', data.liked ? 'true' : 'false');
    btn.querySelector('.heart').textContent = data.liked ? '♥' : '♡';
    btn.querySelector('.like-count').textContent = data.count;

  } catch (err) {
    console.error(err);
    alert('通信に失敗しました');
  }
});
