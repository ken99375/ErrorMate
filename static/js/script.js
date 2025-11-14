document.addEventListener("DOMContentLoaded", () => {
  const menu = document.querySelector(".hamburger-menu");
  const overlay = document.querySelector(".overlay");
  const navMenu = document.querySelector(".nav-menu");
  const navLinks = document.querySelectorAll(".nav-menu a");

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
});



document.getElementById("ai-tag-btn").addEventListener("click", async () => {
    const title = document.getElementById("code").value;   // ←タイトル
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