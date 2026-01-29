document.addEventListener("DOMContentLoaded", () => {

  // ====================================================
  // 1. ハンバーガーメニュー
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
  // 2. タグ管理（手動＋AI 共通）
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

  if (tagList && tagsHidden) {

    const getTagsArray = () =>
      tagsHidden.value
        ? tagsHidden.value.split(",").filter(t => t !== "")
        : [];

    const setTagsArray = (tags) => {
      tagsHidden.value = tags.join(",");
      renderTags();
    };

    const renderTags = () => {
      tagList.innerHTML = "";
      getTagsArray().forEach((tag, index) => {
        const span = document.createElement("span");
        span.className = "tag-chip";
        span.innerHTML = `#${tag} <i class="fa-solid fa-xmark ms-1"></i>`;

        span.querySelector("i").addEventListener("click", () => {
          const tags = getTagsArray();
          tags.splice(index, 1);
          setTagsArray(tags);
        });

        tagList.appendChild(span);
      });
    };

    renderTags();

    // 手動タグ追加
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

      tagInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          tagAddBtn.click();
        }
      });
    }

    // AIタグ生成
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

          setTagsArray(data.tags.slice(0, 5));
          tagStatus.textContent = "タグを生成しました";
        } catch (e) {
          console.error(e);
          tagStatus.textContent = "タグ生成に失敗しました";
        }
      });
    }
  }

  // ====================================================
  // 3. いいねボタン
  // ====================================================
  const likeButtons = document.querySelectorAll(".like-btn");
  likeButtons.forEach(button => {
    button.addEventListener("click", () => {
      button.classList.toggle("liked");
    });
  });

  // ====================================================
  // 4. 言語種別比率（円グラフ）
  // ====================================================
  const chartCanvas = document.getElementById("languageChart");

  if (chartCanvas && typeof Chart !== "undefined") {
    fetch("/personal/api/language_ratio")
      .then(res => {
        if (!res.ok) throw new Error("API error");
        return res.json();
      })
      .then(data => {
        new Chart(chartCanvas.getContext("2d"), {
          type: "pie",
          data: {
            labels: Object.keys(data),
            datasets: [{
              data: Object.values(data)
            }]
          },
          options: {
            plugins: {
              legend: {
                position: "right"
              }
            }
          }
        });
      })
      .catch(err => {
        console.error("言語比率グラフ取得失敗:", err);
      });
  }

});
