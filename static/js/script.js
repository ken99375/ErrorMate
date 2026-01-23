document.addEventListener("DOMContentLoaded", () => {

    // ====================================================
    // 1. ハンバーガーメニューの処理
    // ====================================================
    const menu = document.querySelector(".hamburger-menu");
    const overlay = document.querySelector(".overlay");
    const navMenu = document.querySelector(".nav-menu");
    const navLinks = document.querySelectorAll(".nav-menu a");

    if (menu && overlay && navMenu) {
        menu.addEventListener("click", () => {
            const isActive = menu.classList.toggle("active");
            overlay.classList.toggle("active");
            navMenu.classList.toggle("active");

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
            const statusEl = document.getElementById("tag-status");
            const codeEl = document.getElementById("code");
            const messageEl = document.getElementById("message");
            const titleInput = document.querySelector('input[name="title"]') || document.getElementById("title");

            // 必須要素が一つでも欠けていたら中断
            if (!statusEl || !codeEl || !messageEl) {
                console.warn("AI生成に必要な要素が見つかりません");
                return;
            }

            const title = titleInput ? titleInput.value : "";
            const code = codeEl.value;
            const message = messageEl.value;

            if (!code && !message) {
                statusEl.textContent = "コードかメッセージを入力してください";
                return;
            }

            statusEl.textContent = "AIがタグ考え中…";
            aiTagBtn.disabled = true;

            try {
                // Flask側のAPIへ送信
                const res = await fetch("/api/generate_tags", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, code, message })
                });

                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

                const data = await res.json();

                if (data.tags && data.tags.length > 0) {
                    const tagInput = document.getElementById("tagText");
                    const tagAddBtn = document.getElementById("tagAdd");

                    if (tagInput && tagAddBtn) {
                        data.tags.forEach(tag => {
                            tagInput.value = tag.replace(/^#/, '');
                            tagAddBtn.click(); // 下の「3. タグ追加の処理」を呼び出す
                        });
                        tagInput.value = "";
                        statusEl.textContent = "タグ生成完了！";
                    }
                } else {
                    statusEl.textContent = "タグの候補が見つかりませんでした";
                }
            } catch (e) {
                console.error("AI Tag Generation Error:", e);
                statusEl.textContent = "サーバーとの通信に失敗しました";
            } finally {
                aiTagBtn.disabled = false;
            }
        });
    }

    // ====================================================
    // 3. タグ追加の処理 (チップ表示機能)
    // ====================================================
    const tagInput = document.getElementById("tagText");
    const tagAddBtn = document.getElementById("tagAdd");
    const tagList = document.getElementById("tagList");
    const tagsHidden = document.getElementById("tagsHidden");

    if (tagAddBtn && tagInput && tagList && tagsHidden) {
        // 現在保存されているタグを取得してリスト化
        const getTagsArray = () => tagsHidden.value ? tagsHidden.value.split(',').filter(t => t !== "") : [];

        const renderTags = () => {
            const tagsArray = getTagsArray();
            tagList.innerHTML = '';
            tagsArray.forEach((tag, index) => {
                const chip = document.createElement('span');
                chip.className = 'tag-chip';
                chip.innerHTML = `#${tag} <i class="fa-solid fa-xmark ms-1" style="cursor:pointer;"></i>`;
                
                chip.querySelector('i').addEventListener('click', () => {
                    const currentTags = getTagsArray();
                    currentTags.splice(index, 1);
                    tagsHidden.value = currentTags.join(',');
                    renderTags();
                });
                
                tagList.appendChild(chip);
            });
        };

        tagAddBtn.addEventListener('click', () => {
            const rawValue = tagInput.value.trim();
            if (rawValue === "") return;

            const tagsArray = getTagsArray();
            const newTags = rawValue.split(',').map(t => t.trim().replace(/\s+/g, '_')).filter(t => t !== "");
            
            newTags.forEach(tag => {
                if (tagsArray.length < 10 && !tagsArray.includes(tag)) {
                    tagsArray.push(tag);
                }
            });

            tagsHidden.value = tagsArray.join(',');
            tagInput.value = "";
            renderTags();
        });

        tagInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                tagAddBtn.click();
            }
        });

        renderTags();
    }

    // ====================================================
    // 4. いいねボタンの処理 
    // ====================================================
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('liked');
        });
    });

});