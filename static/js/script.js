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
    // 2. AIタグ生成の処理 
    // ====================================================
    const aiTagBtn = document.getElementById("ai-tag-btn");
    
    if (aiTagBtn) {
        aiTagBtn.addEventListener("click", async () => {
            // ★修正1: タイトルなどの取得元IDが正しいか確認してください
            // (画面では「エラーコード」のIDが code で、「エラータイトル」は title かもしれません)
            // もしタイトル入力欄の name="title" の ID がない場合は、HTML側で id="title" を追加してください
            const titleInput = document.querySelector('input[name="title"]'); 
            const title = titleInput ? titleInput.value : "";
            
            const code = document.getElementById("code").value; // ここでコードを取得
            const message = document.getElementById("message").value;
            const statusEl = document.getElementById("tag-status");

            statusEl.textContent = "AIがタグ考え中…";

            try {
                // APIへ送信（title も送るように修正）
                const res = await fetch("/api/generate_tags", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, code, message }) // codeも含めると精度が上がります
                });

                const data = await res.json();

                if (data.tags && data.tags.length > 0) {
                    // ★修正2: チップ表示機能と連携する
                    const tagInput = document.getElementById("tagText"); // 入力欄
                    const tagAddBtn = document.getElementById("tagAdd"); // ＋ボタン

                    // 生成されたタグを1つずつ順番に追加処理する
                    data.tags.forEach(tag => {
                        tagInput.value = tag; // 入力欄にセット
                        tagAddBtn.click();    // ＋ボタンをプログラムで押す
                    });
                    
                    // 入力欄をクリア
                    tagInput.value = "";
                    statusEl.textContent = "タグ生成完了！";
                } else {
                    statusEl.textContent = "タグ生成失敗（候補なし）";
                }
            } catch (e) {
                console.error(e);
                statusEl.textContent = "エラーが発生しました";
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