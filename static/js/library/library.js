
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

document.addEventListener("click", (e) => {
  if (e.target.closest(".dash-nav-links a")) {
    try {
      sessionStorage.removeItem("renote:libraryScroll");
    } catch (err) {}
  }
});

(function initLibraryFilters() {
  const filterTabs = document.getElementById("filterTabs");
  const libraryGrid = document.getElementById("libraryGrid");
  const statusFilterSelect = document.getElementById("statusFilterSelect");
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

  const STATUS_OPTIONS = {
    all: [
      { value: "all", label: "All Statuses" },
      { value: "in_progress", label: "Watching / Reading" },
      { value: "planned", label: "Plan to Watch / Read" },
      { value: "completed", label: "Completed" },
      { value: "on hold", label: "On Hold" },
      { value: "dropped", label: "Dropped" },
    ],
    watch: [
      { value: "all", label: "All Statuses" },
      { value: "watching", label: "Watching" },
      { value: "plan to watch", label: "Plan to Watch" },
      { value: "completed", label: "Completed" },
      { value: "on hold", label: "On Hold" },
      { value: "dropped", label: "Dropped" },
    ],
    read: [
      { value: "all", label: "All Statuses" },
      { value: "reading", label: "Reading" },
      { value: "plan to read", label: "Plan to Read" },
      { value: "completed", label: "Completed" },
      { value: "on hold", label: "On Hold" },
      { value: "dropped", label: "Dropped" },
    ],
  };

  const LIBRARY_SCROLL_KEY = "renote:libraryScroll";
  let currentType = "all";
  let currentGenre = "all";
  let currentStatus = "all";

  function buildLibraryReturnUrl() {
    const params = new URLSearchParams();
    if (currentType && currentType !== "all") params.set("tab", currentType);
    if (currentStatus && currentStatus !== "all") params.set("status", currentStatus);
    if (currentGenre && currentGenre !== "all") params.set("genre", currentGenre);
    const query = params.toString();
    const basePath = window.location.pathname || "/library/";
    return query ? `${basePath}?${query}` : basePath;
  }

  function syncUrlAndCardLinks() {
    const returnUrl = buildLibraryReturnUrl();
    if (window.history && typeof window.history.replaceState === "function") {
      window.history.replaceState(
        { tab: currentType, status: currentStatus, genre: currentGenre },
        "",
        returnUrl
      );
    }

    const basePath = window.location.pathname || "/library/";
    const hasActiveFilters = returnUrl !== basePath;
    libraryGrid.querySelectorAll(".card-cover-link, .card-title-link").forEach((link) => {
      if (!link.dataset.baseHref) {
        link.dataset.baseHref = link.getAttribute("href") || "";
      }
      const baseHref = link.dataset.baseHref;
      if (!baseHref) return;
      link.setAttribute(
        "href",
        hasActiveFilters ? `${baseHref}?back=${encodeURIComponent(returnUrl)}` : baseHref
      );
    });
  }

  function getStatusGroup(mediaType) {
    if (mediaType === "all") return "all";
    if (mediaType === "manga" || mediaType === "novel" || mediaType === "light novel") {
      return "read";
    }
    return "watch";
  }

  function normalizeStatusForType(statusVal, mediaType) {
    const val = (statusVal || "all").toLowerCase().trim();
    const group = getStatusGroup(mediaType);

    let mapped = val;
    if (group === "all") {
      if (val === "watching" || val === "reading") mapped = "in_progress";
      else if (val === "plan to watch" || val === "plan to read") mapped = "planned";
    } else if (group === "watch") {
      if (val === "in_progress" || val === "reading") mapped = "watching";
      else if (val === "planned" || val === "plan to read") mapped = "plan to watch";
    } else if (group === "read") {
      if (val === "in_progress" || val === "watching") mapped = "reading";
      else if (val === "planned" || val === "plan to watch") mapped = "plan to read";
    }

    const validValues = STATUS_OPTIONS[group].map((opt) => opt.value);
    return validValues.includes(mapped) ? mapped : "all";
  }

  function updateStatusControls(mediaType) {
    if (!statusFilterSelect) return;

    const group = getStatusGroup(mediaType);
    const optionsList = STATUS_OPTIONS[group] || STATUS_OPTIONS.all;
    currentStatus = normalizeStatusForType(currentStatus, mediaType);

    statusFilterSelect.innerHTML = "";
    optionsList.forEach((item) => {
      const opt = document.createElement("option");
      opt.value = item.value;
      opt.textContent = item.label;
      if (item.value === currentStatus) {
        opt.selected = true;
      }
      statusFilterSelect.appendChild(opt);
    });
    statusFilterSelect.value = currentStatus;
  }

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

  function statusMatchesCard(cardStatus) {
    if (currentStatus === "all") return true;
    if (currentStatus === "in_progress") {
      return cardStatus === "watching" || cardStatus === "reading";
    }
    if (currentStatus === "planned") {
      return cardStatus === "plan to watch" || cardStatus === "plan to read";
    }
    return cardStatus === currentStatus;
  }

  function applyFilters() {
    const cards = libraryGrid.querySelectorAll(".media-card");
    let matchCount = 0;

    cards.forEach((card) => {
      const cardType = (card.dataset.type || "").toLowerCase().trim();
      const cardStatus = (card.dataset.status || "").toLowerCase().trim();
      const cardGenresRaw = (card.dataset.genres || "").toLowerCase();
      
      const cardGenres = cardGenresRaw
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const typeMatches = currentType === "all" || cardType === currentType;
      const statusMatches = statusMatchesCard(cardStatus);
      const genreMatches =
        currentGenre === "all" ||
        cardGenres.some((cg) => cg === currentGenre || cg.includes(currentGenre) || currentGenre.includes(cg));

      const isVisible = typeMatches && statusMatches && genreMatches;
      card.style.display = isVisible ? "" : "none";
      if (isVisible) matchCount++;
    });

    if (noMatchState) {
      noMatchState.style.display = matchCount === 0 && cards.length > 0 ? "block" : "none";
    }

    syncUrlAndCardLinks();
  }

  function setLibraryTab(typeVal) {
    currentType = (typeVal || "all").toLowerCase().trim();

    filterTabs.querySelectorAll(".tab").forEach((tab) => {
      tab.classList.toggle("active", (tab.dataset.filter || "").toLowerCase() === currentType);
    });

    updateStatusControls(currentType);
    updateGenreControls(currentType);

    applyFilters();
  }

  function setLibraryStatus(statusVal) {
    currentStatus = normalizeStatusForType(statusVal, currentType);

    if (statusFilterSelect) {
      statusFilterSelect.value = currentStatus;
    }

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

  if (statusFilterSelect) {
    statusFilterSelect.addEventListener("change", () => {
      setLibraryStatus(statusFilterSelect.value);
    });
  }

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

  libraryGrid.addEventListener("click", (e) => {
    const link = e.target.closest(".card-cover-link, .card-title-link");
    if (!link) return;
    try {
      sessionStorage.setItem(
        LIBRARY_SCROLL_KEY,
        JSON.stringify({ url: buildLibraryReturnUrl(), y: window.scrollY || 0 })
      );
    } catch (err) {}
  });

  const urlParams = new URLSearchParams(window.location.search);
  const initialTab = urlParams.get("tab") || urlParams.get("type") || urlParams.get("filter") || window.location.hash.replace("#", "");
  const initialGenre = urlParams.get("genre");
  const initialStatus = urlParams.get("status");

  if (initialTab) {
    setLibraryTab(initialTab);
  }
  if (initialStatus) {
    setLibraryStatus(initialStatus);
  }
  if (initialGenre) {
    setLibraryGenre(initialGenre);
  }
  if (!initialTab && !initialStatus && !initialGenre) {
    syncUrlAndCardLinks();
  }

  try {
    const rawScroll = sessionStorage.getItem(LIBRARY_SCROLL_KEY);
    if (rawScroll) {
      sessionStorage.removeItem(LIBRARY_SCROLL_KEY);
      const saved = JSON.parse(rawScroll);
      if (saved && saved.url === buildLibraryReturnUrl() && typeof saved.y === "number" && saved.y > 0) {
        const scrollFn = () => window.scrollTo(0, saved.y);
        if (typeof requestAnimationFrame === "function") {
          requestAnimationFrame(scrollFn);
        } else {
          scrollFn();
        }
      }
    }
  } catch (err) {}
})();
