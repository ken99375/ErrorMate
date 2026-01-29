document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.like-btn');
  if (!btn) return;

  if (btn.dataset.auth !== '1') {
    location.href = btn.dataset.login || '/auth/login';
    return;
  }

  const cardId = btn.dataset.card;

  try {
    const res = await fetch(`/share/card/${cardId}/like`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'fetch' },
      credentials: 'same-origin'
    });

    if (!res.ok) throw new Error('bad response');
    const data = await res.json();

    const icon = btn.querySelector('.fa-icon');

    if (data.liked) {
      icon.classList.remove('fa-regular');
      icon.classList.add('fa-solid');
      btn.classList.add('liked');
      btn.setAttribute('aria-pressed', 'true');
    } else {
      icon.classList.remove('fa-solid');
      icon.classList.add('fa-regular');
      btn.classList.remove('liked');
      btn.setAttribute('aria-pressed', 'false');
    }

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


/* global bootstrap */

document.addEventListener('click', (e) => {
  const btn = e.target.closest('.js-open-delete');
  if (!btn) return;

  const action = btn.dataset.action;

  const form = document.getElementById('deleteConfirmForm');
  if (form) form.action = action;


  const modalEl = document.getElementById('deleteConfirmModal');
  if (modalEl) new bootstrap.Modal(modalEl).show();
});
