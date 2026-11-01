
document.addEventListener("DOMContentLoaded", () => {
  const mediaDetailShell = document.getElementById("mediaDetailShell");
  if (!mediaDetailShell) return;

  const mediaId = mediaDetailShell.dataset.mediaId;
  const updateUrl = mediaDetailShell.dataset.updateUrl;
  const csrfToken = mediaDetailShell.dataset.csrf;

  const syncIndicator = document.getElementById("syncIndicator");
  let syncTimer = null;

  function showSyncFeedback(msg = "Saved!") {
    if (!syncIndicator) return;
    syncIndicator.textContent = `✓ ${msg}`;
    syncIndicator.classList.add("visible");
    clearTimeout(syncTimer);
    syncTimer = setTimeout(() => {
      syncIndicator.classList.remove("visible");
    }, 2200);
  }

  async function postLogUpdate(payload) {
    try {
      const resp = await fetch(updateUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}`);
      }

      const result = await resp.json();
      showSyncFeedback();
      return result;
    } catch (err) {
      console.error("Failed to update log:", err);
      showSyncFeedback("Update failed");
      return null;
    }
  }

  const favoriteBtn = document.getElementById("favoriteToggleBtn");
  if (favoriteBtn) {
    favoriteBtn.addEventListener("click", async () => {
      const willBeActive = !favoriteBtn.classList.contains("active");
      favoriteBtn.classList.toggle("active", willBeActive);
      const favLabel = favoriteBtn.querySelector(".fav-label");
      if (favLabel) {
        favLabel.textContent = willBeActive ? "Favorited" : "Favorite";
      }

      const res = await postLogUpdate({ action: "toggle_favorite" });
      if (res && res.is_favorite !== undefined) {
        favoriteBtn.classList.toggle("active", res.is_favorite);
        if (favLabel) {
          favLabel.textContent = res.is_favorite ? "Favorited" : "Favorite";
        }
      }
    });
  }

  const rewatchValEl = document.getElementById("rewatchVal");
  const btnIncRewatch = document.getElementById("btnIncRewatch");
  const btnDecRewatch = document.getElementById("btnDecRewatch");

  if (btnIncRewatch && rewatchValEl) {
    btnIncRewatch.addEventListener("click", async () => {
      let cur = parseInt(rewatchValEl.textContent, 10) || 0;
      rewatchValEl.textContent = cur + 1;
      rewatchValEl.style.transform = "scale(1.2)";
      setTimeout(() => (rewatchValEl.style.transform = "scale(1)"), 180);

      const res = await postLogUpdate({ action: "increment_rewatch" });
      if (res && res.rewatch_count !== undefined) {
        rewatchValEl.textContent = res.rewatch_count;
      }
    });
  }

  if (btnDecRewatch && rewatchValEl) {
    btnDecRewatch.addEventListener("click", async () => {
      let cur = parseInt(rewatchValEl.textContent, 10) || 0;
      if (cur <= 0) return;
      rewatchValEl.textContent = Math.max(0, cur - 1);
      rewatchValEl.style.transform = "scale(0.85)";
      setTimeout(() => (rewatchValEl.style.transform = "scale(1)"), 180);

      const res = await postLogUpdate({ action: "decrement_rewatch" });
      if (res && res.rewatch_count !== undefined) {
        rewatchValEl.textContent = res.rewatch_count;
      }
    });
  }

  const statusBtns = document.querySelectorAll(".btn-status-toggle");
  statusBtns.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const newStatus = btn.dataset.status;
      statusBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const metaStatusPill = document.getElementById("metaStatusPill");
      if (metaStatusPill) {
        metaStatusPill.textContent = btn.textContent.trim();
        metaStatusPill.className = `meta-chip status-chip status-${newStatus.replace(/\s+/g, "-")}`;
      }

      await postLogUpdate({ action: "set_status", status: newStatus });
    });
  });

  const starBtns = document.querySelectorAll(".star-btn");
  const ratingBadge = document.getElementById("ratingScoreBadge");
  const clearRateBtn = document.getElementById("clearRateBtn");
  let currentRating = parseInt(mediaDetailShell.dataset.currentRating, 10) || 0;

  function renderStars(score) {
    starBtns.forEach((btn) => {
      const val = parseInt(btn.dataset.value, 10);
      btn.classList.toggle("active", val <= score);
      btn.classList.remove("hover-active");
    });

    if (ratingBadge) {
      ratingBadge.textContent = score > 0 ? `★ ${score} / 5` : "Unrated";
    }
  }

  starBtns.forEach((btn) => {
    btn.addEventListener("mouseenter", () => {
      const hoverVal = parseInt(btn.dataset.value, 10);
      starBtns.forEach((b) => {
        const val = parseInt(b.dataset.value, 10);
        b.classList.toggle("hover-active", val <= hoverVal);
      });
    });

    btn.addEventListener("mouseleave", () => {
      starBtns.forEach((b) => b.classList.remove("hover-active"));
    });

    btn.addEventListener("click", async () => {
      const clickedVal = parseInt(btn.dataset.value, 10);
      
      const nextVal = currentRating === clickedVal ? 0 : clickedVal;
      currentRating = nextVal;
      renderStars(currentRating);
      mediaDetailShell.dataset.currentRating = currentRating;

      await postLogUpdate({
        action: "set_rate",
        personal_rate: currentRating > 0 ? currentRating : null,
      });
    });
  });

  if (clearRateBtn) {
    clearRateBtn.addEventListener("click", async () => {
      currentRating = 0;
      renderStars(0);
      mediaDetailShell.dataset.currentRating = 0;
      await postLogUpdate({ action: "set_rate", personal_rate: null });
    });
  }

  const noteTextarea = document.getElementById("journalNoteText");
  const saveNoteBtn = document.getElementById("saveNoteBtn");

  if (saveNoteBtn && noteTextarea) {
    saveNoteBtn.addEventListener("click", async () => {
      const noteContent = noteTextarea.value.trim();
      saveNoteBtn.disabled = true;
      saveNoteBtn.textContent = "Saving...";

      const res = await postLogUpdate({
        action: "save_note",
        media_note: noteContent,
      });

      saveNoteBtn.disabled = false;
      saveNoteBtn.innerHTML = `<span>Save Note</span>`;
      showSyncFeedback("Note saved!");
    });
  }

  renderStars(currentRating);
});
