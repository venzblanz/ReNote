// ---- profile dropdown (same pattern as home.js) ----
const profileMenu = document.getElementById("profileMenu");
const profileTrigger = document.getElementById("profileTrigger");

if (profileTrigger) {
  profileTrigger.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = profileMenu.classList.toggle("open");
    profileTrigger.setAttribute("aria-expanded", isOpen);
  });

  document.addEventListener("click", (e) => {
    if (!profileMenu.contains(e.target)) {
      profileMenu.classList.remove("open");
      profileTrigger.setAttribute("aria-expanded", "false");
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      profileMenu.classList.remove("open");
      profileTrigger.setAttribute("aria-expanded", "false");
    }
  });
}

// ---- library tab filtering (client-side, library.html only) ----
const filterTabs = document.getElementById("filterTabs");
const libraryGrid = document.getElementById("libraryGrid");

if (filterTabs && libraryGrid) {
  filterTabs.addEventListener("click", (e) => {
    const btn = e.target.closest(".tab");
    if (!btn) return;

    filterTabs.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");

    const filter = btn.dataset.filter;
    libraryGrid.querySelectorAll(".media-card").forEach((card) => {
      const matches = filter === "all" || card.dataset.type === filter;
      card.style.display = matches ? "" : "none";
    });
  });
}
