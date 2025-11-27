document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.like-btn');
  if (!btn) return;

  // 未ログインならログインページへ
  if (btn.dataset.auth !== '1') {
    const login = btn.dataset.login || '/auth/login';
    /* global location*/ 
    location.href = login;
    return;
  }

  const cardId = btn.dataset.card;
  try {
            /* global fetch */
    const res = await fetch(`/share/like/${cardId}`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'fetch' },
      credentials: 'same-origin'
    });
    if (!res.ok) throw new Error('bad response');
    const data = await res.json(); // { liked: true/false, count: number }

    btn.setAttribute('aria-pressed', data.liked ? 'true' : 'false');
    btn.querySelector('.heart').textContent = data.liked ? '♥' : '♡';
    btn.querySelector('.like-count').textContent = data.count;
  } catch (err) {
    console.error(err);
  }
});
