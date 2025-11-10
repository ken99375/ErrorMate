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
