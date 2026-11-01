// =====================================================================
// ReNote — Library Interactions & Tab Filtering
// =====================================================================

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

// ---- library tab filtering (client-side, library.html) ----
const filterTabs = document.getElementById("filterTabs");
const libraryGrid = document.getElementById("libraryGrid");

function setLibraryTab(filterValue) {
  if (!filterTabs || !libraryGrid) return;
  const targetFilter = (filterValue || "all").toLowerCase();

  const tabBtn = filterTabs.querySelector(`.tab[data-filter="${targetFilter}"]`);
  if (tabBtn) {
    filterTabs.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tabBtn.classList.add("active");
  }

  libraryGrid.querySelectorAll(".media-card").forEach((card) => {
    const cardType = (card.dataset.type || "").toLowerCase();
    const matches = targetFilter === "all" || cardType === targetFilter;
    card.style.display = matches ? "" : "none";
  });
}

if (filterTabs && libraryGrid) {
  filterTabs.addEventListener("click", (e) => {
    const btn = e.target.closest(".tab");
    if (!btn) return;
    setLibraryTab(btn.dataset.filter);
  });

  // Check URL parameters on load: e.g. /library/?tab=anime or /library/?filter=anime or #anime
  const urlParams = new URLSearchParams(window.location.search);
  const initialTab = urlParams.get("tab") || urlParams.get("filter") || window.location.hash.replace("#", "");
  if (initialTab) {
    setLibraryTab(initialTab);
  }
}
