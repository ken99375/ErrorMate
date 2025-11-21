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
    // (DOMCotenntLoaded内に移動し、要素の存在チェックを追加)
    // ====================================================
    const aiTagBtn = document.getElementById("ai-tag-btn");
    
    if (aiTagBtn) {
        aiTagBtn.addEventListener("click", async () => {
            const title = document.getElementById("code").value;
            const message = document.getElementById("message").value;
            const statusEl = document.getElementById("tag-status");

            statusEl.textContent = "AIがタグ考え中…";

            const res = await fetch("/api/generate_tags", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, message })
            });

            const data = await res.json();

            if (data.tags) {
                document.getElementById("tags").value = data.tags.join(", ");
                statusEl.textContent = "タグ生成完了！";
            } else {
                statusEl.textContent = "タグ生成失敗";
            }
        });
    }

    // ====================================================
    // 3. タグ追加の処理
    // ====================================================
    const container = document.getElementById("tag-container");
    const addBtn = document.getElementById("add-tag-btn");

    if (container && addBtn) {
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
    // 4. いいねボタンの処理 ✨ これがメイン ✨
    // ====================================================
    const likeButtons = document.querySelectorAll('.like-btn');

    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('liked');
        });
    });

});