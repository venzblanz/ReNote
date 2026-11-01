
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

(function initLibraryFilters() {
  const filterTabs = document.getElementById("filterTabs");
  const libraryGrid = document.getElementById("libraryGrid");
  const genreFilterSelect = document.getElementById("genreFilterSelect");
  const genreChipsRow = document.getElementById("genreChipsRow");
  const noMatchState = document.getElementById("noMatchState");
  const mediaGenresDataEl = document.getElementById("mediaGenresData");

  if (!filterTabs || !libraryGrid) return;

  let mediaGenres = {};
  if (mediaGenresDataEl) {
    try {
      mediaGenres = JSON.parse(mediaGenresDataEl.textContent || "{}");
    } catch (e) {
      console.warn("Failed to parse media genres", e);
    }
  }

  let currentType = "all";
  let currentGenre = "all";

  function updateGenreControls(mediaType) {
    const genresList = mediaGenres[mediaType] || mediaGenres["all"] || [];

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
      
      const hasGenre = currentGenre === "all" || genresList.some((g) => g.toLowerCase() === currentGenre);
      if (!hasGenre) {
        currentGenre = "all";
        genreFilterSelect.value = "all";
      }
    }

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

  function applyFilters() {
    const cards = libraryGrid.querySelectorAll(".media-card");
    let matchCount = 0;

    cards.forEach((card) => {
      const cardType = (card.dataset.type || "").toLowerCase().trim();
      const cardGenresRaw = (card.dataset.genres || "").toLowerCase();
      
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

  function setLibraryTab(typeVal) {
    currentType = (typeVal || "all").toLowerCase().trim();

    filterTabs.querySelectorAll(".tab").forEach((tab) => {
      tab.classList.toggle("active", (tab.dataset.filter || "").toLowerCase() === currentType);
    });

    updateGenreControls(currentType);

    applyFilters();
  }

  function setLibraryGenre(genreVal) {
    currentGenre = (genreVal || "all").toLowerCase().trim();

    if (genreFilterSelect) {
      genreFilterSelect.value = currentGenre;
    }

    if (genreChipsRow) {
      genreChipsRow.querySelectorAll(".genre-chip").forEach((chip) => {
        chip.classList.toggle("active", (chip.dataset.genre || "").toLowerCase() === currentGenre);
      });
    }

    applyFilters();
  }

  filterTabs.addEventListener("click", (e) => {
    const btn = e.target.closest(".tab");
    if (!btn) return;
    setLibraryTab(btn.dataset.filter);
  });

  if (genreFilterSelect) {
    genreFilterSelect.addEventListener("change", () => {
      setLibraryGenre(genreFilterSelect.value);
    });
  }

  if (genreChipsRow) {
    genreChipsRow.addEventListener("click", (e) => {
      const chip = e.target.closest(".genre-chip");
      if (!chip) return;
      setLibraryGenre(chip.dataset.genre);
    });
  }

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
