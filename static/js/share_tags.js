    /* static/js/share_tags.js */
    /* タグ入力UI（＋で追加・クリックで削除・hiddenにCSV保存） */
    (() => {
    const MAX_TAGS = 10;

    // 必須要素のID
    const IDS = {
        list: 'tagList',       // タグの見た目（チップ）を並べるコンテナ
        input: 'tagText',      // 追加用のテキスト入力
        addBtn: 'tagAdd',      // 追加ボタン（＋）
        hidden: 'tagsHidden'   // サーバ送信用 hidden（CSV）
    };

    let els = {};
    let tags = [];

    function q(id) {
        return document.getElementById(id);
    }

    function normalizeTag(s) {
        // 前後空白除去 → 連続空白はアンダースコア化 → 先頭末尾の # は除去
        const trimmed = (s || '').trim().replace(/\s+/g, '_');
        return trimmed.replace(/^#+/, '').replace(/#+$/, '');
    }

    function syncHidden() {
        els.hidden.value = tags.join(',');
    }

    function render() {
        els.list.innerHTML = '';
        tags.forEach((t, i) => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'tag-chip';
        chip.textContent = '#' + t;
        chip.title = 'クリックで削除';
        chip.addEventListener('click', () => {
            tags.splice(i, 1);
            syncHidden();
            render();
        });
        els.list.appendChild(chip);
        });
    }

    function addFromInput() {
        const raw = els.input.value;
        if (!raw || !raw.trim()) return;

        // カンマ区切りで一括追加も許可
        raw.split(',').forEach(piece => {
        const t = normalizeTag(piece);
        if (!t) return;
        if (tags.includes(t)) return;            // 重複スキップ
        if (tags.length >= MAX_TAGS) return;     // 上限
        tags.push(t);
        });

        els.input.value = '';
        syncHidden();
        render();
        els.input.focus();
    }

    function loadInitial() {
        // hidden に初期値（CSV）があれば反映
        const initial = (els.hidden.value || '')
        .split(',')
        .map(s => normalizeTag(s))
        .filter(Boolean);

        // 重複除去して上限まで
        tags = Array.from(new Set(initial)).slice(0, MAX_TAGS);
        syncHidden();
        render();
    }

    function bind() {
        els.addBtn.addEventListener('click', addFromInput);

        // Enterキーで追加
        els.input.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addFromInput();
        }
        });

        // スペースで確定したい場合は下を有効化
        // els.input.addEventListener('keydown', e => {
        //   if (e.key === ' ') {
        //     e.preventDefault();
        //     addFromInput();
        //   }
        // });
    }

    function init() {
        els = {
        list: q(IDS.list),
        input: q(IDS.input),
        addBtn: q(IDS.addBtn),
        hidden: q(IDS.hidden)
        };
        // 必須要素がないページでは何もしない
        if (!els.list || !els.input || !els.addBtn || !els.hidden) return;

        loadInitial();
        bind();
    }

    // 自動初期化
    window.addEventListener('DOMContentLoaded', init);

    // 必要なら外から再初期化できるように
    window.ShareTags = { init };
    })();
