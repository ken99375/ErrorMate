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


document.addEventListener('click', (e) => {
  const btn = e.target.closest('.comment-form button[type="submit"], .reply-form button[type="submit"]');
  if (!btn) return;

  if (btn.disabled) {
    e.preventDefault();
    return;
  }

  btn.disabled = true;
});

document.addEventListener('click', (e) => {
  const btn = e.target.closest('.js-open-delete');
  if (!btn) return;

  const action = btn.dataset.action;
  const title  = btn.dataset.title || '';

  const form = document.getElementById('deleteConfirmForm');
  if (form) form.action = action;

  const label = document.getElementById('deleteTargetTitle');
  if (label) label.textContent = title ? `対象: ${title}` : '';

/* global bootstrap */

  const modalEl = document.getElementById('deleteConfirmModal');
  if (modalEl) new bootstrap.Modal(modalEl).show();
});
