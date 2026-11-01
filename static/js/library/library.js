// =====================================================================
// ReNote — Library Interactions & Multi-Dimensional Filtering
// =====================================================================

// ---- profile dropdown ----
const profileMenu = document.getElementById("profileMenu");
const profileTrigger = document.getElementById("profileTrigger");

if (profileTrigger && profileMenu) {
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

// ---- library filtering (Media Type + Dynamic Genre) ----
(function initLibraryFilters() {
  const filterTabs = document.getElementById("filterTabs");
  const libraryGrid = document.getElementById("libraryGrid");
  const genreFilterSelect = document.getElementById("genreFilterSelect");
  const genreChipsRow = document.getElementById("genreChipsRow");
  const noMatchState = document.getElementById("noMatchState");
  const mediaGenresDataEl = document.getElementById("mediaGenresData");

  if (!filterTabs || !libraryGrid) return;

  // Load genres mapping
  let mediaGenres = {};
  if (mediaGenresDataEl) {
    try {
      mediaGenres = JSON.parse(mediaGenresDataEl.textContent || "{}");
    } catch (e) {
      console.warn("Failed to parse media genres", e);
    }
  }

  // Active filter state
  let currentType = "all";
  let currentGenre = "all";

  // Repopulate genre dropdown and chips for the active media type
  function updateGenreControls(mediaType) {
    const genresList = mediaGenres[mediaType] || mediaGenres["all"] || [];

    // 1. Update Dropdown
    if (genreFilterSelect) {
      genreFilterSelect.innerHTML = '<option value="all">All Genres</option>';
      genresList.forEach((g) => {
        const opt = document.createElement("option");
        opt.value = g.toLowerCase();
        opt.textContent = g;
        if (opt.value === currentGenre) {
          opt.selected = true;
        }
        genreFilterSelect.appendChild(opt);
      });
      // If previous genre is not in new list, reset to 'all'
      const hasGenre = currentGenre === "all" || genresList.some((g) => g.toLowerCase() === currentGenre);
      if (!hasGenre) {
        currentGenre = "all";
        genreFilterSelect.value = "all";
      }
    }

    // 2. Update Quick Chips
    if (genreChipsRow) {
      genreChipsRow.innerHTML = '<button type="button" class="genre-chip active" data-genre="all">All</button>';
      genresList.forEach((g) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `genre-chip ${g.toLowerCase() === currentGenre ? "active" : ""}`;
        btn.dataset.genre = g.toLowerCase();
        btn.textContent = g;
        genreChipsRow.appendChild(btn);
      });
    }
  }

  // Filter cards on grid
  function applyFilters() {
    const cards = libraryGrid.querySelectorAll(".media-card");
    let matchCount = 0;

    cards.forEach((card) => {
      const cardType = (card.dataset.type || "").toLowerCase().trim();
      const cardGenresRaw = (card.dataset.genres || "").toLowerCase();
      // card.dataset.genres format: "action,drama,fantasy,"
      const cardGenres = cardGenresRaw
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const typeMatches = currentType === "all" || cardType === currentType;
      const genreMatches =
        currentGenre === "all" ||
        cardGenres.some((cg) => cg === currentGenre || cg.includes(currentGenre) || currentGenre.includes(cg));

      const isVisible = typeMatches && genreMatches;
      card.style.display = isVisible ? "" : "none";
      if (isVisible) matchCount++;
    });

    if (noMatchState) {
      noMatchState.style.display = matchCount === 0 && cards.length > 0 ? "block" : "none";
    }
  }

  // Set Media Type Tab
  function setLibraryTab(typeVal) {
    currentType = (typeVal || "all").toLowerCase().trim();

    // Sync tab button active class
    filterTabs.querySelectorAll(".tab").forEach((tab) => {
      tab.classList.toggle("active", (tab.dataset.filter || "").toLowerCase() === currentType);
    });

    // Update available genres for this type
    updateGenreControls(currentType);

    // Apply combined filter
    applyFilters();
  }

  // Set Genre Filter
  function setLibraryGenre(genreVal) {
    currentGenre = (genreVal || "all").toLowerCase().trim();

    // Sync select dropdown
    if (genreFilterSelect) {
      genreFilterSelect.value = currentGenre;
    }

    // Sync quick chips
    if (genreChipsRow) {
      genreChipsRow.querySelectorAll(".genre-chip").forEach((chip) => {
        chip.classList.toggle("active", (chip.dataset.genre || "").toLowerCase() === currentGenre);
      });
    }

    applyFilters();
  }

  // Listeners: Tabs
  filterTabs.addEventListener("click", (e) => {
    const btn = e.target.closest(".tab");
    if (!btn) return;
    setLibraryTab(btn.dataset.filter);
  });

  // Listeners: Genre Select Dropdown
  if (genreFilterSelect) {
    genreFilterSelect.addEventListener("change", () => {
      setLibraryGenre(genreFilterSelect.value);
    });
  }

  // Listeners: Quick Genre Chips
  if (genreChipsRow) {
    genreChipsRow.addEventListener("click", (e) => {
      const chip = e.target.closest(".genre-chip");
      if (!chip) return;
      setLibraryGenre(chip.dataset.genre);
    });
  }

  // Check initial URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const initialTab = urlParams.get("tab") || urlParams.get("type") || urlParams.get("filter") || window.location.hash.replace("#", "");
  const initialGenre = urlParams.get("genre");

  if (initialTab) {
    setLibraryTab(initialTab);
  }
  if (initialGenre) {
    setLibraryGenre(initialGenre);
  }
})();
