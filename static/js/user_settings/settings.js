
const navItems = document.querySelectorAll(".settings-nav-item");
const sections = document.querySelectorAll(".settings-section");

function showSection(name) {
  navItems.forEach((item) => item.classList.toggle("active", item.dataset.section === name));
  sections.forEach((section) => section.classList.toggle("active", section.dataset.section === name));
}

navItems.forEach((item) => {
  item.addEventListener("click", () => {
    showSection(item.dataset.section);
    history.replaceState(null, "", `#${item.dataset.section}`);
  });
});

const initialSection = window.location.hash.replace("#", "");
if (initialSection && document.querySelector(`.settings-nav-item[data-section="${initialSection}"]`)) {
  showSection(initialSection);
}

const avatarButtons = document.querySelectorAll(".avatar-option-btn");
const selectedAvatarInput = document.getElementById("selectedAvatarInput");
const avatarPreview = document.getElementById("avatarPreview");

if (avatarButtons.length && selectedAvatarInput) {
  avatarButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const av = btn.dataset.avatar;
      avatarButtons.forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      if (selectedAvatarInput.value !== av) {
        selectedAvatarInput.value = av;
        markDirty();
      }
      if (avatarPreview) {
        const img = btn.querySelector("img");
        if (img) {
          avatarPreview.src = img.src;
        }
      }
    });
  });
}

const bioField = document.getElementById("prof-bio");
const bioCount = document.getElementById("bioCount");
const BIO_LIMIT = 200;

if (bioField && bioCount) {
  function updateBioCount() {
    const len = Math.min(bioField.value.length, BIO_LIMIT);
    bioCount.textContent = `${len} / ${BIO_LIMIT}`;
  }
  updateBioCount();
  bioField.addEventListener("input", updateBioCount);
}

const settingsForm = document.getElementById("settingsForm");
const saveBar = document.getElementById("saveBar");
const discardBtn = document.getElementById("discardChanges");
let dirty = false;

function markDirty() {
  if (dirty || !saveBar) return;
  dirty = true;
  saveBar.classList.add("visible");
}

function clearDirty() {
  dirty = false;
  if (saveBar) {
    saveBar.classList.remove("visible");
  }
}

if (settingsForm) {
  settingsForm.addEventListener("input", markDirty);
  settingsForm.addEventListener("change", markDirty);
}

if (discardBtn && settingsForm) {
  discardBtn.addEventListener("click", () => {
    settingsForm.reset();
    if (bioField && bioCount) {
      const len = Math.min(bioField.value.length, BIO_LIMIT);
      bioCount.textContent = `${len} / ${BIO_LIMIT}`;
    }
    clearDirty();
  });
}

window.addEventListener("beforeunload", (e) => {
  if (dirty) {
    e.preventDefault();
    e.returnValue = "";
  }
});

if (settingsForm) {
  settingsForm.addEventListener("submit", () => {
    dirty = false;
  });
}

const deactivateBtn = document.getElementById("deactivateBtn");
const deactivateAccountForm = document.getElementById("deactivateAccountForm");

if (deactivateBtn && deactivateAccountForm) {
  deactivateBtn.addEventListener("click", () => {
    const confirmed = confirm(
      "Are you sure you want to temporarily deactivate your account? You can reactivate anytime by logging back in."
    );
    if (confirmed) {
      deactivateAccountForm.submit();
    }
  });
}

const deleteModal = document.getElementById("deleteModal");
const openDeleteModalBtn = document.getElementById("openDeleteModal");
const cancelDeleteBtn = document.getElementById("cancelDelete");
const confirmDeleteBtn = document.getElementById("confirmDelete");
const deleteConfirmInput = document.getElementById("deleteConfirmInput");
const deleteAccountForm = document.getElementById("deleteAccountForm");

function openModal() {
  if (!deleteModal || !deleteConfirmInput || !confirmDeleteBtn) return;
  deleteModal.classList.add("open");
  deleteConfirmInput.value = "";
  confirmDeleteBtn.disabled = true;
  setTimeout(() => deleteConfirmInput.focus(), 60);
}

function closeModal() {
  if (!deleteModal) return;
  deleteModal.classList.remove("open");
}

if (openDeleteModalBtn) openDeleteModalBtn.addEventListener("click", openModal);
if (cancelDeleteBtn) cancelDeleteBtn.addEventListener("click", closeModal);

if (deleteModal) {
  deleteModal.addEventListener("click", (e) => {
    if (e.target === deleteModal) closeModal();
  });
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && deleteModal && deleteModal.classList.contains("open")) {
    closeModal();
  }
});

if (deleteConfirmInput && confirmDeleteBtn) {
  deleteConfirmInput.addEventListener("input", () => {
    confirmDeleteBtn.disabled = deleteConfirmInput.value.trim() !== "DELETE";
  });
}

const btnSyncNow = document.getElementById("btnSyncNow");
const syncResultBox = document.getElementById("syncResultBox");
const btnSyncText = document.getElementById("btnSyncText");

if (btnSyncNow){
  btnSyncNow.addEventListener("click", async () => {
    const syncUrl = btnSyncNow.dataset.url;
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

    btnSyncNow.disabled = true;
    if (btnSyncText) btnSyncText.textContent = "Syncing..."
    if (syncResultBox) {
      syncResultBox.style.display = "block";
      syncResultBox.style.background = "rgba(168, 86, 247, 0.15)";
      syncResultBox.style.color = "#E9D5FF"
      syncResultBox.textContent = "Connecting to online database and Syncing data..."
    }

    try {
      const response = await fetch(syncUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();

      if(response.ok && data.success){
        if(syncResultBox){
          syncResultBox.style.background = "rgba(34, 197, 94, 0.15)";
          syncResultBox.style.color = "#86EFAC";
          syncResultBox.textContent = `${data.message || "Sync completed successfully!"}`;
        }
      }else{
        if (syncResultBox) {
          syncResultBox.style.background = "rgba(239, 68, 68, 0.15)";
          syncResultBox.style.color = "#FCA5A5";
          syncResultBox.textContent = `${data.error || "Failed to sync with online database."}`;
        }
      } 
    } catch (err) {
      if (syncResultBox) {
        syncResultBox.style.background = "rgba(239, 68, 68, 0.15)";
        syncResultBox.style.color = "#FCA5A5";
        syncResultBox.textContent = "Network Error: Could not reach the database. Please check your internet connection.";
      }
    } finally {
      btnSyncNow.disabled = false;
      if(btnSyncText) btnSyncText.textContent = "Sync with Cloud";
    }
  });
}