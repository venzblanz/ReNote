// =====================================================================
// ReNote — Anime Media Dashboard Interactions
// Spotlight Switcher, Modal Picker & Library Feed
// =====================================================================

document.addEventListener("DOMContentLoaded", () => {
  // ---- Spotlight Data (3 Featured Shows) ----
  const spotlights = [
    {
      title: "Solo Leveling",
      jpTitle: "俺だけレベルアップな件 (Ore dake Reberuappu na Ken)",
      desc: "In a world where hunters must battle deadly monsters to protect humanity, Sung Jin-woo, an underdog hunter ridiculed as the weakest of all mankind, awakens to an extraordinary system that unlocks an infinite path to level up alone into the supreme Shadow Monarch.",
      image: "/static/images/hero_character_purple.jpg",
      rating: "4.9",
      popularity: "475K",
      genres: ["Animation", "Action", "Adventure", "Dark Fantasy"],
      tagline: "From the weakest hunter in the world to the supreme Shadow Monarch reigning over darkness.",
      creator: "Chugong / DUBU (REDICE Studio)",
      stars: "Taito Ban, Genta Nakamura, Reina Ueda",
      sliderNum: "01"
    },
    {
      title: "Jujutsu Kaisen",
      jpTitle: "呪術廻戦 (Satoru Gojo — Hollow Purple)",
      desc: "A boy swallows a cursed talisman - the finger of a demon - and becomes cursed himself. Enter Satoru Gojo, the strongest jujutsu sorcerer in modern history, who bends space itself with Infinity and obliterates threats with Hollow Purple.",
      image: "/static/images/gojo_purple.jpg",
      rating: "4.8",
      popularity: "620K",
      genres: ["Animation", "Action", "Supernatural", "Shounen"],
      tagline: "Throughout heaven and earth, I alone am the honored one.",
      creator: "Gege Akutami (Studio MAPPA)",
      stars: "Yuichi Nakamura, Junya Enoki, Yuma Uchida",
      sliderNum: "02"
    },
    {
      title: "Naruto Uzumaki",
      jpTitle: "うずまきナルト (Sage of Six Paths Mode)",
      desc: "Naruto Uzumaki is a shinobi of Konohagakure's Uzumaki clan. Shrouded in blazing purple sage chakra and the power of the Nine-Tails, he fought through isolation to achieve his dream of becoming Hokage and saving the ninja world.",
      image: "/static/images/naruto_purple.jpg",
      rating: "4.7",
      popularity: "890K",
      genres: ["Animation", "Action", "Adventure", "Martial Arts"],
      tagline: "I never go back on my word — that is my ninja way!",
      creator: "Masashi Kishimoto (Studio Pierrot)",
      stars: "Junko Takeuchi, Noriaki Sugiyama, Chie Nakamura",
      sliderNum: "03"
    }
  ];

  let currentSpotlightIdx = 0;

  const spotlightTitle = document.getElementById("spotlightTitle");
  const spotlightJp = document.getElementById("spotlightJp");
  const spotlightDesc = document.getElementById("spotlightDesc");
  const characterImg = document.getElementById("characterImg");
  const spotlightRating = document.getElementById("spotlightRating");
  const spotlightPop = document.getElementById("spotlightPop");
  const spotlightGenres = document.getElementById("spotlightGenres");
  const spotlightTagline = document.getElementById("spotlightTagline");
  const spotlightCreator = document.getElementById("spotlightCreator");
  const spotlightStars = document.getElementById("spotlightStars");
  const sliderNum = document.getElementById("sliderNum");
  const sliderPip = document.getElementById("sliderPip");
  const dockCards = document.querySelectorAll(".dock-card");

  function setSpotlight(idx) {
    currentSpotlightIdx = idx;
    const data = spotlights[idx];

    // Smooth transition
    characterImg.style.opacity = "0";
    characterImg.style.transform = "scale(0.96)";

    setTimeout(() => {
      spotlightTitle.textContent = data.title;
      spotlightJp.textContent = data.jpTitle;
      spotlightDesc.textContent = data.desc;
      characterImg.src = data.image;
      spotlightRating.textContent = data.rating;
      spotlightPop.textContent = data.popularity;
      spotlightTagline.textContent = data.tagline;
      spotlightCreator.textContent = data.creator;
      spotlightStars.textContent = data.stars;
      sliderNum.textContent = data.sliderNum;

      // Genres
      spotlightGenres.innerHTML = data.genres.map(g => `<span class="genre-pill">${g}</span>`).join("");

      // Slider pip position (0, 22px, 44px)
      sliderPip.style.top = `${idx * 22}px`;

      // Active mini card
      dockCards.forEach((c, i) => c.classList.toggle("active", i === idx));

      characterImg.style.opacity = "1";
      characterImg.style.transform = "scale(1)";
    }, 180);
  }

  dockCards.forEach((card, idx) => {
    card.addEventListener("click", () => {
      setSpotlight(idx);
    });
  });

  // ---- Profile Menu Dropdown ----
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

  // ---- Interactive Rate Button ----
  const rateBtn = document.getElementById("rateBtn");
  const rateLabel = document.getElementById("rateLabel");
  let userRated = false;
  if (rateBtn) {
    rateBtn.addEventListener("click", () => {
      userRated = !userRated;
      rateLabel.textContent = userRated ? "5.0 ★ Rated" : "Rate";
      rateBtn.style.color = userRated ? "#FCD34D" : "#D8B4FE";
    });
  }

  // ---- "Pick for Me" Modal / Drawer ----
  const pickerModal = document.getElementById("pickerModal");
  const navRandomBtn = document.getElementById("navRandomBtn");
  const heroPickBtn = document.getElementById("heroPickBtn");
  const openPickerBtn = document.getElementById("openPickerBtn");
  const closePickerBtn = document.getElementById("closePickerBtn");
  const spinPickBtn = document.getElementById("spinPickBtn");
  const modalPickResult = document.getElementById("modalPickResult");

  function openModal() {
    pickerModal.classList.add("open");
    modalPickResult.textContent = "";
  }
  function closeModal() {
    pickerModal.classList.remove("open");
  }

  if (navRandomBtn) navRandomBtn.addEventListener("click", (e) => { e.preventDefault(); openModal(); });
  if (heroPickBtn) heroPickBtn.addEventListener("click", openModal);
  if (openPickerBtn) openPickerBtn.addEventListener("click", openModal);
  if (closePickerBtn) closePickerBtn.addEventListener("click", closeModal);

  if (pickerModal) {
    pickerModal.addEventListener("click", (e) => {
      if (e.target === pickerModal) closeModal();
    });
  }

  // Random pick library data
  const pickLibrary = [
    { title: "Solo Leveling", type: "Anime", desc: "Shadow Monarch hunter leveling up alone." },
    { title: "Jujutsu Kaisen", type: "Anime", desc: "Sorcery battle with Sukuna and Satoru Gojo." },
    { title: "Attack on Titan", type: "Anime", desc: "Humanity's survival battle against the Titans." },
    { title: "Berserk", type: "Manga", desc: "The Black Swordsman Guts defying fate and demons." },
    { title: "Bleach: Thousand-Year Blood War", type: "Anime", desc: "Soul Reapers vs the Quincy Empire." },
    { title: "Chainsaw Man", type: "Anime / Manga", desc: "Denji living as a devil hunter with Pochita." },
    { title: "Vinland Saga", type: "Anime", desc: "Thorfinn's transformative historical Viking epic." },
    { title: "Steins;Gate", type: "Anime", desc: "Time travel, cause-and-effect, and science fiction masterpiece." },
    { title: "Neon Genesis Evangelion", type: "Anime", desc: "Psychological mecha thriller and apocalyptic deconstruction." },
    { title: "Hunter x Hunter", type: "Anime", desc: "Gon Freecss setting out to become a legendary Hunter." }
  ];

  let spinTimer = null;
  if (spinPickBtn) {
    spinPickBtn.addEventListener("click", () => {
      clearInterval(spinTimer);
      modalPickResult.classList.add("is-spinning");

      const chosen = pickLibrary[Math.floor(Math.random() * pickLibrary.length)];
      let ticks = 0;

      spinTimer = setInterval(() => {
        const temp = pickLibrary[Math.floor(Math.random() * pickLibrary.length)];
        modalPickResult.textContent = `Rolling: ${temp.title} (${temp.type})...`;
        ticks++;
        if (ticks > 9) {
          clearInterval(spinTimer);
          modalPickResult.classList.remove("is-spinning");
          modalPickResult.innerHTML = `
            <div>
              <span style="display:block; font-size: 0.85rem; color: #A855F7; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;">Tonight's Selected Pick</span>
              <strong style="color: #fff; font-size: 1.6rem;">${chosen.title}</strong>
              <span style="display:block; font-size: 0.875rem; color: #D8B4FE; font-weight: 500; margin-top: 4px;">${chosen.type} — ${chosen.desc}</span>
            </div>
          `;
        }
      }, 80);
    });
  }

  // ---- Library Feed Items & Status ----
  const userLibrary = [
    { title: "Solo Leveling", type: "Anime", rating: 5, status: "watching", count: "3 rewatches", img: "/static/images/hero_character_purple.jpg" },
    { title: "Jujutsu Kaisen", type: "Anime", rating: 5, status: "watching", count: "2 rewatches", img: "/static/images/gojo_purple.jpg" },
    { title: "Naruto Shippuden", type: "Anime", rating: 5, status: "completed", count: "4 rewatches", img: "/static/images/naruto_purple.jpg" },
    { title: "Berserk", type: "Manga", rating: 5, status: "reading", count: "4 rereads", img: "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600&q=80" },
    { title: "Dune", type: "Novel", rating: 4, status: "completed", count: "1 reread", img: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80" },
    { title: "Attack on Titan", type: "Anime", rating: 5, status: "completed", count: "3 rewatches", img: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600&q=80" },
    { title: "Vinland Saga", type: "Anime", rating: 4, status: "plan-to-watch", count: "2 rewatches", img: "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&q=80" },
    { title: "Chainsaw Man", type: "Manga", rating: 5, status: "reading", count: "2 rereads", img: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&q=80" },
  ];

  function renderStars(n) {
    return "★".repeat(n) + "☆".repeat(Math.max(0, 5 - n));
  }

  const libraryGrid = document.getElementById("libraryGrid");
  if (libraryGrid) {
    function renderGrid(filter) {
      libraryGrid.innerHTML = "";
      const filtered = filter === "all" ? userLibrary : userLibrary.filter(i => i.type.toLowerCase() === filter.toLowerCase());

      filtered.forEach((item) => {
        const card = document.createElement("div");
        card.className = "media-card";
        card.setAttribute("data-type", item.type);

        card.innerHTML = `
          <div class="cover">
            <img src="${item.img}" alt="${item.title}" onerror="this.src='/static/images/hero_character_purple.jpg'">
            <span class="type-badge">${item.type}</span>
          </div>
          <div class="card-body">
            <h3 class="card-title">${item.title}</h3>
            <span class="status-pill status-${item.status}">${item.status.replace('-', ' ')}</span>
            <div class="card-meta">
              <span class="stars">${renderStars(item.rating)}</span>
              <span class="rewatch">${item.count}</span>
            </div>
          </div>
        `;
        libraryGrid.appendChild(card);
      });
    }

    renderGrid("all");

    // Tab filtering
    const filterTabs = document.getElementById("filterTabs");
    if (filterTabs) {
      filterTabs.addEventListener("click", (e) => {
        const btn = e.target.closest(".tab-pill");
        if (!btn) return;
        filterTabs.querySelectorAll(".tab-pill").forEach(t => t.classList.remove("active"));
        btn.classList.add("active");
        renderGrid(btn.dataset.filter);
      });
    }
  }

  // ---- Rewatch Leaderboard ----
  const leaderboardEl = document.getElementById("leaderboard");
  if (leaderboardEl) {
    const leaders = [
      { title: "Berserk", sub: "Manga", count: "Reread × 4" },
      { title: "Attack on Titan", sub: "Anime", count: "Rewatch × 3" },
      { title: "Solo Leveling", sub: "Anime", count: "Rewatch × 3" },
      { title: "Jujutsu Kaisen", sub: "Anime", count: "Rewatch × 2" },
      { title: "Naruto Shippuden", sub: "Anime", count: "Rewatch × 4" }
    ];

    leaderboardEl.innerHTML = leaders.map((item, i) => `
      <li>
        <span class="lb-rank">0${i + 1}</span>
        <span class="lb-title">${item.title}<span>${item.sub}</span></span>
        <span class="lb-count">${item.count}</span>
      </li>
    `).join("");
  }
});
