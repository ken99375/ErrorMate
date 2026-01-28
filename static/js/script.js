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

document.addEventListener("DOMContentLoaded", () => {

  // ====================================================
  // 共通要素取得（null ガード前提）
  // ====================================================
  const tagBtn = document.getElementById("ai-tag-btn");
  const tagList = document.getElementById("tagList");
  const tagStatus = document.getElementById("tag-status");
  const tagsHidden = document.getElementById("tagsHidden");

  const titleEl = document.getElementById("title");
  const codeEl = document.getElementById("code");
  const messageEl = document.getElementById("message");

  const tagInput = document.getElementById("tagText");
  const tagAddBtn = document.getElementById("tagAdd");

  if (!tagList || !tagsHidden) return;

  // ====================================================
  // タグ管理ユーティリティ
  // ====================================================
  const getTagsArray = () =>
    tagsHidden.value
      ? tagsHidden.value.split(",").filter(t => t !== "")
      : [];

  const setTagsArray = (tags) => {
    tagsHidden.value = tags.join(",");
    renderManualTags();
  };

  // ====================================================
  // 手動タグ描画
  // ====================================================
  const renderManualTags = () => {
    tagList.innerHTML = "";
    getTagsArray().forEach((tag, index) => {
      const span = document.createElement("span");
      span.className = "tag-chip";
      span.textContent = `#${tag}`;

      span.addEventListener("click", () => {
        const tags = getTagsArray();
        tags.splice(index, 1);
        setTagsArray(tags);
      });

      tagList.appendChild(span);
    });
  };

  renderManualTags();

  // ====================================================
  // 手動タグ追加
  // ====================================================
  if (tagAddBtn && tagInput) {
    tagAddBtn.addEventListener("click", () => {
      const raw = tagInput.value.trim();
      if (!raw) return;

      const current = getTagsArray();
      raw.split(",")
        .map(t => t.trim().toLowerCase())
        .filter(t => t && !current.includes(t))
        .slice(0, 10 - current.length)
        .forEach(t => current.push(t));

      setTagsArray(current);
      tagInput.value = "";
    });
  }

  // ====================================================
  // AIタグ描画（AI専用）
  // ====================================================
  const renderAiTags = (tags) => {
    setTagsArray(tags.slice(0, 5));
  };

  // ====================================================
  // AIタグ生成
  // ====================================================
  if (tagBtn && titleEl && codeEl && messageEl) {
    tagBtn.addEventListener("click", async () => {
      tagStatus.textContent = "タグ生成中…";

      try {
        const res = await fetch("/api/ai/tags", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: titleEl.value,
            code: codeEl.value,
            message: messageEl.value
          })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error);

        renderAiTags(data.tags);
        tagStatus.textContent = "タグを生成しました";
      } catch (e) {
        console.error(e);
        tagStatus.textContent = "タグ生成に失敗しました";
      }
    });
  }

});

    // ====================================================
    // 3. タグ追加の処理 (チップ表示機能)
    // ====================================================
    const tagInput = document.getElementById("tagText");
    const tagAddBtn = document.getElementById("tagAdd");

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