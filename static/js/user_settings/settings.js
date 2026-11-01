
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
