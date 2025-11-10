// ダミーのステップカード配列（DBの代わり）
const cards = [];
let nextId = 1;

const screenList   = document.getElementById('screen-list');
const screenEditor = document.getElementById('screen-editor');

const emptyArea = document.getElementById('empty_area');
const cardList  = document.getElementById('card_list');
const toolbar   = document.getElementById('toolbar');

const form = document.getElementById('step_form');

function showScreen(screen) {
  screenList.classList.remove('active');
  screenEditor.classList.remove('active');
  screen.classList.add('active');
}

function renderList() {
  // 件数によって「カード一覧」と「0件メッセージ」を出し分け
  if (cards.length === 0) {
    emptyArea.style.display = 'block';
    cardList.style.display  = 'none';
    cardList.innerHTML = '';

    // カード0件のときは右上の新規作成は非表示
    if (toolbar) toolbar.style.display = 'none';
    return;
  }

  emptyArea.style.display = 'none';
  cardList.style.display  = 'grid';
  cardList.innerHTML = '';

  // カードが1件以上あるときは右上の新規作成を表示
  if (toolbar) toolbar.style.display = 'flex';

  cards.forEach(card => {
    const div = document.createElement('div');
    div.className = 'card-item';

    const title = document.createElement('div');
    title.className = 'card-title';
    title.textContent = card.title || '(無題のエラー)';

    const summary = document.createElement('div');
    summary.className = 'card-summary';
    const msg = card.message || card.errorCode || '';
    summary.textContent = msg.length > 60 ? msg.slice(0, 57) + '...' : msg;

    const actions = document.createElement('div');
    actions.className = 'card-actions';

    // 詳細ボタン
    const detailBtn = document.createElement('button');
    detailBtn.textContent = '詳細';
    detailBtn.name = 'link_detail';
    detailBtn.addEventListener('click', () => {
      alert(
        '【詳細】\n\n' +
        'タイトル: '    + (card.title || '') + '\n\n' +
        'エラーコード:\n' + (card.errorCode || '') + '\n\n' +
        '修正コード:\n'  + (card.fixCode || '') + '\n\n' +
        'エラーメッセージ:\n' + (card.message || '') + '\n\n' +
        '実装結果:\n'    + (card.result || '')
      );
    });

    // 共有ボタン
    const shareBtn = document.createElement('button');
    shareBtn.textContent = '共有';
    shareBtn.name = 'link_share';
    shareBtn.addEventListener('click', () => {
      // ここはダミー。実際は共有リンク生成処理に置き換え
      const dummyUrl = 'https://errormate.example/step/' + card.id;
      alert('共有リンクの例:\n' + dummyUrl);
    });

    actions.appendChild(detailBtn);
    actions.appendChild(shareBtn);

    div.appendChild(title);
    div.appendChild(summary);
    div.appendChild(actions);

    cardList.appendChild(div);
  });
}

// 新規作成リンク（一覧画面右上）
document.getElementById('link_create')
  .addEventListener('click', () => {
    form.reset();
    showScreen(screenEditor);
  });

// 新規作成リンク（0件メッセージ内）
document.getElementById('link_create_empty')
  .addEventListener('click', () => {
    form.reset();
    showScreen(screenEditor);
  });

// 一覧に戻る
document.getElementById('link_list')
  .addEventListener('click', () => {
    showScreen(screenList);
  });

// 保存処理（DBなし・メモリに積むだけ）
form.addEventListener('submit', (e) => {
  e.preventDefault();

  const card = {
    id: nextId++,
    title:    document.getElementById('text_title').value.trim(),
    errorCode:document.getElementById('text_error').value,
    fixCode:  document.getElementById('text_fixcode').value,
    message:  document.getElementById('text_message').value,
    result:   document.getElementById('text_result').value
  };

  cards.push(card);

  renderList();
  showScreen(screenList);
});

// 初期表示
renderList();
