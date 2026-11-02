
document.addEventListener("DOMContentLoaded", () => {
  
  const spotlights = [
    {
      title: "ReNote",
      jpTitle: "月夜のメディアカタログ (Celestial Moon Collection)",
      desc: "Every story that moves you deserves a place in the night sky. ReNote reflects your journey through fiction, giving you a personal sanctuary to record, track, and relive the anime, manga, novels, and films that left their mark.",
      image: "/static/images/moon.png",
      rating: "5.0",
      genres: ["Anime", "Manga", "Movie", "Novel"],
      tagline: "Manage your collection seamlessly — cached media info means zero repeated API calls.",
      creator: "Cached in media_catalog",
      stars: "Community & You",
      sliderNum: "01"
    },
    {
      title: "Solo Leveling",
      jpTitle: "Ore dake Reberuappu na Ken",
      desc: "In a world where hunters must battle deadly monsters to protect humanity, Sung Jin-woo, an underdog hunter ridiculed as the weakest of all mankind, awakens to an extraordinary system that unlocks an infinite path to level up alone into the supreme Shadow Monarch.",
      image: "/static/images/hero_character_purple.jpg",
      rating: "4.9",
      genres: ["Animation", "Action", "Adventure", "Dark Fantasy"],
      tagline: "From the weakest hunter in the world to the supreme Shadow Monarch reigning over darkness.",
      creator: "Chugong / DUBU (REDICE Studio)",
      stars: "Taito Ban, Genta Nakamura, Reina Ueda",
      sliderNum: "02"
    },
    {
      title: "Jujutsu Kaisen",
      jpTitle: "",
      desc: "A boy swallows a cursed talisman - the finger of a demon - and becomes cursed himself. Enter Satoru Gojo, the strongest jujutsu sorcerer in modern history, who bends space itself with Infinity and obliterates threats with Hollow Purple.",
      image: "/static/images/gojo_purple.jpg",
      rating: "4.8",
      genres: ["Animation", "Action", "Supernatural", "Shounen"],
      tagline: "Throughout heaven and earth, I alone am the honored one.",
      creator: "Gege Akutami (Studio MAPPA)",
      stars: "Yuichi Nakamura, Junya Enoki, Yuma Uchida",
      sliderNum: "03"
    },
    {
      title: "Naruto",
      jpTitle: "",
      desc: "Naruto Uzumaki is a shinobi of Konohagakure's Uzumaki clan. Shrouded in blazing purple sage chakra and the power of the Nine-Tails, he fought through isolation to achieve his dream of becoming Hokage and saving the ninja world.",
      image: "/static/images/naruto_purple.jpg",
      rating: "4.7",
      genres: ["Animation", "Action", "Adventure", "Martial Arts"],
      tagline: "I never go back on my word — that is my ninja way!",
      creator: "Masashi Kishimoto (Studio Pierrot)",
      stars: "Junko Takeuchi, Noriaki Sugiyama, Chie Nakamura",
      sliderNum: "04"
    }
  ];

  let currentSpotlightIdx = 0;

  const spotlightTitle = document.getElementById("spotlightTitle");
  const spotlightJp = document.getElementById("spotlightJp");
  const spotlightDesc = document.getElementById("spotlightDesc");
  const heroMoonImg = document.getElementById("heroMoonImg");
  const spotlightRating = document.getElementById("spotlightRating");
  const spotlightGenres = document.getElementById("spotlightGenres");
  const spotlightTagline = document.getElementById("spotlightTagline");
  const spotlightCreator = document.getElementById("spotlightCreator");
  const spotlightStars = document.getElementById("spotlightStars");
  const sliderNum = document.getElementById("sliderNum");
  const sliderPip = document.getElementById("sliderPip");
  const dockCards = document.querySelectorAll(".dock-card");

  function setSpotlight(idx) {
    if (idx < 0 || idx >= spotlights.length) return;
    currentSpotlightIdx = idx;
    const data = spotlights[idx];

    if (heroMoonImg) {
      heroMoonImg.style.opacity = "0";
      heroMoonImg.style.transform = "scale(0.94)";
    }

    setTimeout(() => {
      if (spotlightTitle) spotlightTitle.textContent = data.title;
      if (spotlightJp) spotlightJp.textContent = data.jpTitle;
      if (spotlightDesc) spotlightDesc.textContent = data.desc;
      if (heroMoonImg) heroMoonImg.src = data.image;
      if (spotlightRating) spotlightRating.textContent = data.rating;
      if (spotlightTagline) spotlightTagline.textContent = data.tagline;
      if (spotlightCreator) spotlightCreator.textContent = data.creator;
      if (spotlightStars) spotlightStars.textContent = data.stars;
      if (sliderNum) sliderNum.textContent = data.sliderNum;

      if (spotlightGenres) {
        spotlightGenres.innerHTML = data.genres.map(g => `<span class="genre-pill">${g}</span>`).join("");
      }

      if (sliderPip) {
        sliderPip.style.top = `${idx * 16}px`;
      }

      dockCards.forEach((c, i) => c.classList.toggle("active", i === idx));

      if (heroMoonImg) {
        heroMoonImg.style.opacity = "1";
        heroMoonImg.style.transform = "scale(1)";
      }
    }, 180);
  }

  dockCards.forEach((card, idx) => {
    card.addEventListener("click", () => {
      setSpotlight(idx);
    });
  });

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

  const rateBtn = document.getElementById("rateBtn");
  const rateLabel = document.getElementById("rateLabel");
  let userRated = false;
  if (rateBtn) {
    rateBtn.addEventListener("click", () => {
      userRated = !userRated;
      if (rateLabel) rateLabel.textContent = userRated ? "5.0 ★ Rated" : "Rate";
      rateBtn.style.color = userRated ? "#FCD34D" : "#D8B4FE";
    });
  }

  const pickerModal = document.getElementById("pickerModal");
  const navRandomBtn = document.getElementById("navRandomBtn");
  const heroPickBtn = document.getElementById("heroPickBtn");
  const closePickerBtn = document.getElementById("closePickerBtn");
  const spinPickBtn = document.getElementById("spinPickBtn");
  const modalPickResult = document.getElementById("modalPickResult");
  const modalFilterType = document.getElementById("modalFilterType");
  const modalFilterStatus = document.getElementById("modalFilterStatus");

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
          <div style="padding: 12px 0;">
            <p style="color: #F87171; margin: 0 0 8px; font-size: 1rem;">Your library is empty.</p>
            <span style="font-size: 0.85rem; color: #D8B4FE;">Add titles from Search & Add Title first to roll a pick!</span>
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
          <div style="padding: 12px 0;">
            <p style="color: #FCD34D; margin: 0 0 6px; font-size: 1rem;">No matching titles in your library.</p>
            <span style="font-size: 0.85rem; color: #D8B4FE;">Try setting the filters to "All Formats" or "Any Status".</span>
          </div>
        `;
        return;
      }

      modalPickResult.classList.add("is-spinning");
      const chosen = pool[Math.floor(Math.random() * pool.length)];
      let ticks = 0;

      spinTimer = setInterval(() => {
        const temp = pool[Math.floor(Math.random() * pool.length)];
        modalPickResult.textContent = `Rolling: ${temp.title} (${temp.type})...`;
        ticks++;
        if (ticks > 8) {
          clearInterval(spinTimer);
          modalPickResult.classList.remove("is-spinning");
          const safeTitle = escapeHtml(chosen.title);
          const safeType = escapeHtml(chosen.type);
          const safeStatus = escapeHtml(chosen.status || "In Library");
          const detailUrl = chosen.url || "#";

          modalPickResult.innerHTML = `
            <a href="${detailUrl}" class="pick-result-card" title="Click to view details for ${safeTitle}">
              ${chosen.img ? `<img src="${chosen.img}" alt="${safeTitle}" class="pick-result-cover">` : '<div class="pick-result-cover placeholder">🎬</div>'}
              <div class="pick-result-info">
                <span class="pick-result-badge">Tonight's Selected Pick</span>
                <strong class="pick-result-title">${safeTitle}</strong>
                <div class="pick-result-meta">
                  <span class="pick-result-type">${safeType}</span>
                  <span class="pick-result-dot">•</span>
                  <span class="pick-result-status">${safeStatus}</span>
                </div>
              </div>
              <div class="pick-result-action">
                <span class="btn-pick-open">
                  <span>View Details</span>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </span>
              </div>
            </a>
          `;
        }
      }, 75);
    });
  }

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
