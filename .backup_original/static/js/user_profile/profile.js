// ---- placeholder data (swap for real DB-driven content in Django) ----
const library = [
  { title: "Attack on Titan", type: "Anime", rating: 4, count: "3 rewatches" },
  { title: "Interstellar",    type: "Movie", rating: 5, count: "2 rewatches" },
  { title: "Berserk",         type: "Manga", rating: 5, count: "4 rereads" },
  { title: "Dune",            type: "Novel", rating: 4, count: "1 reread" },
  { title: "Re:Zero",         type: "Light Novel", rating: 4, count: "1 reread" },
  { title: "Vinland Saga",    type: "Anime", rating: 4, count: "2 rewatches" },
  { title: "Chainsaw Man",    type: "Manga", rating: 5, count: "1 reread" },
  { title: "Parasite",        type: "Movie", rating: 5, count: "1 rewatch" },
];

const colorClasses = ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"];

function stars(n) {
  return "★".repeat(n) + "☆".repeat(5 - n);
}

const grid = document.getElementById("libraryGrid");
const emptyState = document.getElementById("emptyState");

function renderGrid(filter) {
  const items = filter === "all" ? library : library.filter((i) => i.type === filter);
  grid.innerHTML = "";
  items.forEach((item, i) => {
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
  emptyState.hidden = items.length !== 0;
  grid.hidden = items.length === 0;
}
renderGrid("all");

// ---- tab filtering ----
const tabs = document.querySelectorAll(".tab");
tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    renderGrid(tab.dataset.filter);
  });
});

// ---- stats ----
const stats = [
  { value: library.length, label: "Total titles" },
  { value: library.filter((i) => i.type === "Anime").length, label: "Anime watched" },
  { value: library.filter((i) => i.type === "Manga").length, label: "Manga read" },
  { value: library.filter((i) => i.type === "Movie").length, label: "Movies watched" },
  { value: 12, label: "Total rewatches" },
  { value: "Shounen", label: "Favorite genre" },
];
const statsRow = document.getElementById("statsRow");
stats.forEach((s) => {
  const div = document.createElement("div");
  div.className = "stat-card";
  div.innerHTML = `<div class="stat-value">${s.value}</div><div class="stat-label">${s.label}</div>`;
  statsRow.appendChild(div);
});

// ---- favorite genres ----
const genres = ["Shounen", "Sci-Fi", "Slice of Life", "Fantasy", "Psychological"];
const genreTags = document.getElementById("genreTags");
genres.forEach((g) => {
  const span = document.createElement("span");
  span.className = "genre-tag";
  span.textContent = g;
  genreTags.appendChild(span);
});

// ---- recent activity ----
const activity = [
  { title: "Chainsaw Man", sub: "Manga", count: "Finished ch. 150" },
  { title: "Attack on Titan", sub: "Anime", count: "Rewatch · ep 12" },
  { title: "Dune", sub: "Novel", count: "Started" },
  { title: "Interstellar", sub: "Movie", count: "Rewatched" },
];
const activityList = document.getElementById("activityList");
activity.forEach((item, i) => {
  const li = document.createElement("li");
  li.innerHTML = `
    <span class="lb-rank">${i + 1}.</span>
    <span class="lb-title">${item.title}<span>${item.sub}</span></span>
    <span class="lb-count">${item.count}</span>
  `;
  activityList.appendChild(li);
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
