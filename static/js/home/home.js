// ---- placeholder data (swap for real DB-driven content in Django) ----
  const library = [
    { title: "Attack on Titan", type: "Anime",  rating: 4, count: "3 rewatches" },
    { title: "Interstellar",    type: "Movie",  rating: 5, count: "2 rewatches" },
    { title: "Interstellar",    type: "Movie",  rating: 5, count: "2 rewatches" },
    { title: "Berserk",         type: "Manga",  rating: 5, count: "4 rereads"   },
    { title: "Dune",            type: "Novel",  rating: 4, count: "1 reread"    },
    { title: "Re:Zero",         type: "Light Novel", rating: 4, count: "1 reread" },
    { title: "Berserk",         type: "Manga",  rating: 5, count: "3 rereads"   },
    { title: "Vinland Saga",    type: "Anime",  rating: 4, count: "2 rewatches" },
  ];

  const colorClasses = ["c1","c2","c3","c4","c5","c6","c7","c8"];

  function stars(n) {
    return "★".repeat(n) + "☆".repeat(5 - n);
  }

  const grid = document.getElementById("libraryGrid");
  library.forEach((item, i) => {
    const card = document.createElement("div");
    card.className = "media-card";
    card.innerHTML = `
      <div class="cover ${colorClasses[i % colorClasses.length]}" data-type="${item.type}">
        ${item.title}
      </div>
      <div class="card-meta">
        <span class="stars">${stars(item.rating)}</span>
        <span>${item.count}</span>
      </div>
    `;
    grid.appendChild(card);
  });

  const leaders = [
    { title: "Berserk", sub: "Manga", count: "Reread · 4" },
    { title: "Attack on Titan", sub: "Anime", count: "Reread · 3" },
    { title: "Berserk", sub: "Manga", count: "Reread · 2" },
    { title: "Back to the Future", sub: "Movie", count: "Rewatch · 2" },
    { title: "The Genre", sub: "Manga", count: "1" },
    { title: "Attack on Titan", sub: "Anime", count: "1" },
  ];

  const lb = document.getElementById("leaderboard");
  leaders.forEach((item, i) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span class="lb-rank">${i + 1}.</span>
      <span class="lb-title">${item.title}<span>${item.sub}</span></span>
      <span class="lb-count">${item.count}</span>
    `;
    lb.appendChild(li);
  });

  // ---- profile dropdown ----
  const profileMenu = document.getElementById("profileMenu");
  const profileTrigger = document.getElementById("profileTrigger");

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

  // ---- "Pick for me" interaction ----
  const pickBtn = document.getElementById("pickBtn");
  const pickResult = document.getElementById("pickResult");

  pickBtn.addEventListener("click", () => {
    const choice = library[Math.floor(Math.random() * library.length)];
    pickResult.innerHTML = `Spinning… `;
    let ticks = 0;
    const spin = setInterval(() => {
      const random = library[Math.floor(Math.random() * library.length)];
      pickResult.innerHTML = `Spinning… <strong>${random.title}</strong>`;
      ticks++;
      if (ticks > 8) {
        clearInterval(spin);
        pickResult.innerHTML = `Tonight's pick: <strong>${choice.title}</strong> (${choice.type})`;
      }
    }, 90);
  });
