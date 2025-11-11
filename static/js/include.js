// include.js － 部品（partials）を読み込んで差し込む軽量ローダー
(() => {
    const cache = new Map(); // URL -> Promise<string>

    async function load(url) {
        if (cache.has(url)) return cache.get(url);
        const p = fetch(url, { credentials: "same-origin" })
            .then(async (res) => {
                if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
                return await res.text();
            });
        cache.set(url, p);
        return p;
    }

    // 挿入後、含まれている <script> を実行（innerHTMLじゃ動かないため）
    function executeScripts(container) {
        const scripts = container.querySelectorAll("script");
        scripts.forEach((old) => {
            const s = document.createElement("script");
            // type / src / nomodule / defer など最低限を引き継ぐ
            [...old.attributes].forEach(attr => s.setAttribute(attr.name, attr.value));
            if (!old.src) s.textContent = old.textContent;
            old.replaceWith(s);
        });
    }

    // data-include を持つ要素へ読み込み
    async function includeFragments(root = document) {
        const targets = [...root.querySelectorAll("[data-include]")];
        if (targets.length === 0) return;

        await Promise.all(
            targets.map(async (el) => {
                const url = el.getAttribute("data-include");
                try {
                    const html = await load(url);
                    el.innerHTML = html;
                    executeScripts(el);
                    el.dispatchEvent(new CustomEvent("fragment:loaded", { bubbles: true, detail: { url } }));
                } catch (err) {
                    console.warn(`[include.js] ${url} の読み込みに失敗:`, err);
                    el.innerHTML = `<div style="color:#b00020;font-size:12px">パーシャルの読み込みに失敗しました：${escapeHtml(url)}</div>`;
                }
            })
        );
    }

    // サイドバーの active 制御（<a data-key="..."> に .active 付与）
    function markActive(key) {
        if (!key) return;
        document.querySelectorAll(".sidebar [data-key], [data-key]").forEach(a => {
            a.classList.toggle("active", a.getAttribute("data-key") === key);
        });
    }

    // XSSにならないように軽くエスケープ
    function escapeHtml(str) {
        return String(str).replace(/[&<>"']/g, s => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "\"": "&quot;",
            "'": "&#39;"
        }[s]));
    }

    // ページ初期化
    document.addEventListener("DOMContentLoaded", async () => {
        await includeFragments();

        // body に data-active があれば自動で active を反映
        const keyFromBody = document.body.getAttribute("data-active");
        if (keyFromBody) markActive(keyFromBody);

        // 既存 script.js で初期化が必要なら、パーシャル挿入後にここで呼べる
        // 例: if (window.initHeaderMenu) window.initHeaderMenu();
    });

    // 外部からも使えるように公開
    window.EMinclude = { includeFragments, markActive };
    window.setActive = markActive; // 互換API: window.setActive('comments')
})();
