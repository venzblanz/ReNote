document.addEventListener("DOMContentLoaded", () => {
  const spotlights = [
    {
      title: "Solo Leveling",
      jpTitle: "Ore dake Reberuappu na Ken",
      desc: "In a world where hunters battle deadly monsters, Sung Jin-woo awakens to an extraordinary system that unlocks an infinite path to level up alone into the supreme Shadow Monarch.",
      image: "/static/images/hero_character_purple.jpg",
      rating: "4.9",
      genres: ["Animation", "Action", "Dark Fantasy"]
    },
    {
      title: "Jujutsu Kaisen",
      jpTitle: "Jujutsu Kaisen",
      desc: "A boy swallows a cursed talisman and becomes cursed himself. Enter Satoru Gojo, the strongest jujutsu sorcerer in modern history, who bends space with Infinity and Hollow Purple.",
      image: "/static/images/gojo_purple.jpg",
      rating: "4.8",
      genres: ["Animation", "Action", "Supernatural"]
    },
    {
      title: "Naruto",
      jpTitle: "Naruto Shippuden",
      desc: "Naruto Uzumaki is a shinobi of the Uzumaki clan. Shrouded in blazing purple sage chakra and the Nine-Tails, he fought through isolation to achieve his dream of becoming Hokage.",
      image: "/static/images/naruto_purple.jpg",
      rating: "4.7",
      genres: ["Animation", "Action", "Adventure"]
    }
  ];

  let currentSpotlightIdx = 0;

  const spotlightTitle = document.getElementById("spotlightTitle");
  const spotlightJp = document.getElementById("spotlightJp");
  const spotlightDesc = document.getElementById("spotlightDesc");
  const heroMoonImg = document.getElementById("heroMoonImg");
  const spotlightGenres = document.getElementById("spotlightGenres");
  const storyPips = document.querySelectorAll(".story-pip");
  const spotlightPrevBtn = document.getElementById("spotlightPrevBtn");
  const spotlightNextBtn = document.getElementById("spotlightNextBtn");

  function setSpotlight(idx) {
    if (idx < 0) idx = spotlights.length - 1;
    if (idx >= spotlights.length) idx = 0;
    currentSpotlightIdx = idx;
    const data = spotlights[idx];

    if (heroMoonImg) {
      heroMoonImg.style.opacity = "0.4";
      heroMoonImg.style.transform = "scale(1.02)";
    }

    setTimeout(() => {
      if (spotlightTitle) spotlightTitle.textContent = data.title;
      if (spotlightJp) spotlightJp.textContent = data.jpTitle;
      if (spotlightDesc) spotlightDesc.textContent = data.desc;
      if (heroMoonImg) heroMoonImg.src = data.image;

      if (spotlightGenres) {
        spotlightGenres.innerHTML = data.genres.map(g => `<span class="genre-pill">${g}</span>`).join("");
      }

      storyPips.forEach((pip, i) => {
        pip.classList.toggle("active", i === idx);
      });

      if (heroMoonImg) {
        heroMoonImg.style.opacity = "1";
        heroMoonImg.style.transform = "scale(1)";
      }
    }, 150);
  }

  storyPips.forEach((pip) => {
    pip.addEventListener("click", () => {
      const idx = parseInt(pip.dataset.index, 10);
      setSpotlight(idx);
    });
  });

  if (spotlightPrevBtn) {
    spotlightPrevBtn.addEventListener("click", () => setSpotlight(currentSpotlightIdx - 1));
  }
  if (spotlightNextBtn) {
    spotlightNextBtn.addEventListener("click", () => setSpotlight(currentSpotlightIdx + 1));
  }

  // Interactive Chooser Modal & Bottom Sheet
  const pickerModal = document.getElementById("pickerModal");
  const navRandomBtn = document.getElementById("navRandomBtn");
  const heroPickBtn = document.getElementById("heroPickBtn");
  const closePickerBtn = document.getElementById("closePickerBtn");
  const spinPickBtn = document.getElementById("spinPickBtn");
  const modalPickResult = document.getElementById("modalPickResult");
  const modalFilterType = document.getElementById("modalFilterType");
  const modalFilterStatus = document.getElementById("modalFilterStatus");
  const mobileDockPickerBtn = document.getElementById("mobileDockPickerBtn");

  // Segmented chips for format & status
  const formatChips = document.querySelectorAll("#formatChips .filter-chip");
  formatChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      formatChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      if (modalFilterType) modalFilterType.value = chip.dataset.val;
    });
  });

  const statusChips = document.querySelectorAll("#statusChips .filter-chip");
  statusChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      statusChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      if (modalFilterStatus) modalFilterStatus.value = chip.dataset.val;
    });
  });

  function openModal() {
    if (pickerModal) {
      pickerModal.classList.add("open");
      document.body.classList.add("modal-open");
      if (modalPickResult) modalPickResult.textContent = "";
    }
  }

  function closeModal() {
    if (pickerModal) {
      pickerModal.classList.remove("open");
      document.body.classList.remove("modal-open");
    }
  }

  if (navRandomBtn) navRandomBtn.addEventListener("click", (e) => { e.preventDefault(); openModal(); });
  if (mobileDockPickerBtn) mobileDockPickerBtn.addEventListener("click", (e) => { e.preventDefault(); openModal(); });
  if (heroPickBtn) heroPickBtn.addEventListener("click", openModal);
  if (closePickerBtn) closePickerBtn.addEventListener("click", closeModal);

  if (pickerModal) {
    pickerModal.addEventListener("click", (e) => {
      if (e.target === pickerModal) closeModal();
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && pickerModal && pickerModal.classList.contains("open")) {
      closeModal();
    }
  });

  function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/[&<>"']/g, function(m) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }[m];
    });
  }

  function getUserLibraryItems() {
    const cards = document.querySelectorAll("#libraryGrid .media-card");
    const items = [];
    cards.forEach((card) => {
      const titleEl = card.querySelector(".card-title");
      const typeEl = card.querySelector(".type-badge");
      const statusEl = card.querySelector(".status-pill");
      const imgEl = card.querySelector(".cover img");
      const linkEl = card.querySelector("a.card-cover-link, a.card-title-link, a[href*='/library/media/']");
      const detailUrl = card.dataset.detailUrl || (linkEl ? linkEl.getAttribute("href") : "");
      const type = (card.dataset.type || (typeEl ? typeEl.textContent : "")).trim().toLowerCase();
      const status = statusEl ? statusEl.textContent.trim().toLowerCase() : "";
      if (titleEl) {
        items.push({
          title: titleEl.textContent.trim(),
          type: typeEl ? typeEl.textContent.trim() : "Title",
          typeRaw: type,
          status: status,
          img: imgEl ? imgEl.src : "",
          url: detailUrl
        });
      }
    });
    return items;
  }

  let spinTimer = null;
  if (spinPickBtn && modalPickResult) {
    spinPickBtn.addEventListener("click", () => {
      clearInterval(spinTimer);
      const allUserItems = getUserLibraryItems();

      if (allUserItems.length === 0) {
        modalPickResult.innerHTML = `
          <div class="pick-empty-notice">
            <p class="pick-empty-text">Your library is currently empty.</p>
            <span class="pick-empty-sub">Add titles from the catalog first to roll a pick!</span>
          </div>
        `;
        return;
      }

      const typeFilter = modalFilterType ? modalFilterType.value.toLowerCase() : "all";
      const statusFilter = modalFilterStatus ? modalFilterStatus.value.toLowerCase() : "all";

      const pool = allUserItems.filter((item) => {
        const typeMatch = typeFilter === "all" || item.typeRaw === typeFilter;
        const statusMatch = statusFilter === "all" || item.status.includes(statusFilter);
        return typeMatch && statusMatch;
      });

      if (pool.length === 0) {
        modalPickResult.innerHTML = `
          <div class="pick-empty-notice">
            <p class="pick-empty-text">No matching titles found in your library.</p>
            <span class="pick-empty-sub">Try changing the format or status filters.</span>
          </div>
        `;
        return;
      }

      modalPickResult.classList.add("is-spinning");
      const chosen = pool[Math.floor(Math.random() * pool.length)];
      let ticks = 0;

      spinTimer = setInterval(() => {
        const temp = pool[Math.floor(Math.random() * pool.length)];
        modalPickResult.textContent = `Rolling: ${temp.title} (${temp.type})…`;
        ticks++;
        if (ticks > 8) {
          clearInterval(spinTimer);
          modalPickResult.classList.remove("is-spinning");
          const safeTitle = escapeHtml(chosen.title);
          const safeType = escapeHtml(chosen.type);
          const safeStatus = escapeHtml(chosen.status || "In Library");
          const detailUrl = chosen.url || "#";

          modalPickResult.innerHTML = `
            <a href="${detailUrl}" class="pick-result-card" title="Open details for ${safeTitle}">
              ${chosen.img ? `<img src="${chosen.img}" alt="${safeTitle}" class="pick-result-cover">` : '<div class="pick-result-cover placeholder">★</div>'}
              <div class="pick-result-info">
                <span class="pick-result-badge">SELECTED PICK</span>
                <strong class="pick-result-title">${safeTitle}</strong>
                <div class="pick-result-meta">
                  <span class="pick-result-type">${safeType}</span>
                  <span class="pick-result-dot">•</span>
                  <span class="pick-result-status">${safeStatus}</span>
                </div>
              </div>
              <div class="pick-result-action">
                <span class="btn-pick-open">
                  <span>View</span>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </span>
              </div>
            </a>
          `;
        }
      }, 75);
    });
  }

  // Filter tabs for library overview on home
  const filterTabs = document.getElementById("filterTabs");
  const libraryGrid = document.getElementById("libraryGrid");
  const showAllRow = document.getElementById("showAllRow");
  const showAllBtn = document.getElementById("showAllBtn");
  const showAllText = document.getElementById("showAllText");

  function filterLibraryCards(filter) {
    if (!libraryGrid) return;
    const cards = libraryGrid.querySelectorAll(".media-card");
    const normalizedFilter = (filter || "all").toLowerCase();

    let matchingCount = 0;
    let visibleCount = 0;

    cards.forEach((card) => {
      const cardType = (card.dataset.type || "").toLowerCase();
      const matches = normalizedFilter === "all" || cardType === normalizedFilter;

      if (matches) {
        matchingCount++;
        if (visibleCount < 12) {
          card.style.display = "";
          visibleCount++;
        } else {
          card.style.display = "none";
        }
      } else {
        card.style.display = "none";
      }
    });

    if (showAllRow && showAllBtn) {
      if (matchingCount > 12) {
        showAllRow.style.display = "flex";
        const label = normalizedFilter === "all" ? "All Media" : (normalizedFilter.charAt(0).toUpperCase() + normalizedFilter.slice(1));
        if (showAllText) {
          showAllText.textContent = `Show All ${label} (${matchingCount})`;
        }
        showAllBtn.href = `/library/?tab=${encodeURIComponent(normalizedFilter)}`;
      } else {
        showAllRow.style.display = "none";
      }
    }
  }

  filterLibraryCards("all");

  if (filterTabs && libraryGrid) {
    filterTabs.addEventListener("click", (e) => {
      const btn = e.target.closest(".tab-pill");
      if (!btn) return;
      filterTabs.querySelectorAll(".tab-pill").forEach(t => t.classList.remove("active"));
      btn.classList.add("active");

      const filter = (btn.dataset.filter || "all").toLowerCase();
      filterLibraryCards(filter);
    });
  }
});
