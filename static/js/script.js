document.addEventListener("DOMContentLoaded", () => {

    // ====================================================
    // 1. ハンバーガーメニューの処理
    // ====================================================
    const menu = document.querySelector(".hamburger-menu");
    const overlay = document.querySelector(".overlay");
    const navMenu = document.querySelector(".nav-menu");
    const navLinks = document.querySelectorAll(".nav-menu a");

    if (menu) { // 要素が存在するかチェック
        menu.addEventListener("click", () => {
            const isActive = menu.classList.toggle("active");
            overlay.classList.toggle("active");
            navMenu.classList.toggle("active");

            // アニメーション付きでリンクを順番に出す
            if (isActive) {
                navLinks.forEach((link, i) => {
                    setTimeout(() => link.classList.add("show"), i * 80);
                });
            } else {
                navLinks.forEach(link => link.classList.remove("show"));
            }
        });
        
        overlay.addEventListener("click", () => {
            menu.classList.remove("active");
            overlay.classList.remove("active");
            navMenu.classList.remove("active");
            navLinks.forEach(link => link.classList.remove("show"));
        });
    }

// ====================================================
    // 2. AIタグ生成の処理 (入力画面・確認画面 両対応版)
    // ====================================================
    const aiTagBtn = document.getElementById("ai-tag-btn");
    
    if (aiTagBtn) {
        aiTagBtn.addEventListener("click", async () => {
            const statusEl = document.getElementById("tag-status");

            // ★万能な値取得関数: 要素の種類によって取り方を変える
            const getText = (id) => {
                const el = document.getElementById(id);
                if (!el) return "";
                // inputやtextareaならvalue、それ以外ならtextContent
                return (el.tagName === "INPUT" || el.tagName === "TEXTAREA") ? el.value : el.textContent;
            };

            // 1. データの取得
            // タイトルは画面によってIDやnameが違うことがあるため、念入りに探す
            let title = getText("title"); 
            if (!title) {
                // 新規作成画面などで name="text_title" や name="title" の場合
                const titleInput = document.querySelector('input[name="text_title"]') || document.querySelector('input[name="title"]');
                if (titleInput) title = titleInput.value;
            }

            // コードとメッセージを取得（万能関数を使用）
            const code = getText("code"); 
            const message = getText("message");

            // デバッグ用: 何が取れているかコンソールで確認できます
            console.log("AIへ送信:", { title, code, message });

            if (statusEl) statusEl.textContent = "AIがタグ考え中…";

            try {
                // APIへ送信
                const res = await fetch("/api/generate_tags", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, code, message })
                });

                if (!res.ok) throw new Error("API request failed");

                const data = await res.json();

                if (data.tags && data.tags.length > 0) {
                    const tagInput = document.getElementById("tagText"); // タグ入力欄
                    const tagAddBtn = document.getElementById("tagAdd"); // ＋ボタン

                    if (tagInput && tagAddBtn) {
                        // 生成されたタグを1つずつ入力してボタンを押す（既存のタグ追加ロジックを利用）
                        data.tags.forEach(tag => {
                            tagInput.value = tag;
                            tagAddBtn.click();
                        });
                        
                        // 入力欄をクリア
                        tagInput.value = "";
                        if (statusEl) statusEl.textContent = "タグ生成完了！";
                    }
                } else {
                    if (statusEl) statusEl.textContent = "タグ生成失敗（候補なし）";
                }
            } catch (e) {
                console.error(e);
                if (statusEl) statusEl.textContent = "エラーが発生しました";
            }
        });
    }

    // ====================================================
    // 3. タグ追加の処理
    // ====================================================
    const container = document.getElementById("tag-container");
    const addBtn = document.getElementById("add-tag-btn");

    if (container && addBtn) {
        // 既存の click イベントを解除（重複防止）
        const newAddBtn = addBtn.cloneNode(true);
        addBtn.parentNode.replaceChild(newAddBtn, addBtn);

        newAddBtn.addEventListener("click", function (e) {
            e.preventDefault();

            const currentTags = container.querySelectorAll("input[name='tags[]']").length;
            if (currentTags >= 5) {
                alert("タグは最大5個までです。");
                return;
            }

            const input = document.createElement("input");
            input.type = "text";
            input.name = "tags[]";
            input.classList.add("tag-input");
            input.placeholder = "タグを入力";

            container.appendChild(input);
        });
    }

    // ====================================================
    // 4. いいねボタンの処理 
    // ====================================================
    const likeButtons = document.querySelectorAll('.like-btn');

    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // CSSクラス '.liked' をトグル
            this.classList.toggle('liked');
        });
    });

});