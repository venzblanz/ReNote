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

// ---- section switching ----
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

// ---- avatar upload preview ----
const avatarInput = document.getElementById("avatarInput");
const avatarPreview = document.getElementById("avatarPreview");
const removeAvatarBtn = document.getElementById("removeAvatar");

avatarInput.addEventListener("change", () => {
  const file = avatarInput.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    avatarPreview.style.backgroundImage = `url(${e.target.result})`;
    markDirty();
  };
  reader.readAsDataURL(file);
});

removeAvatarBtn.addEventListener("click", () => {
  avatarPreview.style.backgroundImage = "none";
  avatarInput.value = "";
  markDirty();
});

// ---- bio character count ----
const bioField = document.getElementById("prof-bio");
const bioCount = document.getElementById("bioCount");
const BIO_LIMIT = 200;

function updateBioCount() {
  const len = Math.min(bioField.value.length, BIO_LIMIT);
  bioCount.textContent = `${len} / ${BIO_LIMIT}`;
}
updateBioCount();
bioField.addEventListener("input", updateBioCount);

// ---- unsaved changes / save bar ----
const saveBar = document.getElementById("saveBar");
const saveBtn = document.getElementById("saveChanges");
const discardBtn = document.getElementById("discardChanges");
const toast = document.getElementById("toast");

let dirty = false;
const trackedForms = document.querySelectorAll(".settings-section form, form.settings-section");
const initialFormData = new Map();

document.querySelectorAll("form.settings-section").forEach((form) => {
  initialFormData.set(form, new FormData(form));
  form.addEventListener("input", markDirty);
  form.addEventListener("change", markDirty);
});

function markDirty() {
  if (dirty) return;
  dirty = true;
  saveBar.classList.add("visible");
}

function clearDirty() {
  dirty = false;
  saveBar.classList.remove("visible");
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  setTimeout(() => toast.classList.remove("visible"), 2200);
}

saveBtn.addEventListener("click", () => {
  // In production this posts each changed form to its Django view.
  clearDirty();
  showToast("Changes saved");
});

discardBtn.addEventListener("click", () => {
  document.querySelectorAll("form.settings-section").forEach((form) => form.reset());
  updateBioCount();
  avatarPreview.style.backgroundImage = "none";
  clearDirty();
});

window.addEventListener("beforeunload", (e) => {
  if (dirty) {
    e.preventDefault();
    e.returnValue = "";
  }
});

// ---- delete account modal ----
const deleteModal = document.getElementById("deleteModal");
const openDeleteModalBtn = document.getElementById("openDeleteModal");
const cancelDeleteBtn = document.getElementById("cancelDelete");
const confirmDeleteBtn = document.getElementById("confirmDelete");
const deleteConfirmInput = document.getElementById("deleteConfirmInput");

function openModal() {
  deleteModal.classList.add("open");
  deleteConfirmInput.value = "";
  confirmDeleteBtn.disabled = true;
  setTimeout(() => deleteConfirmInput.focus(), 50);
}
function closeModal() {
  deleteModal.classList.remove("open");
}

openDeleteModalBtn.addEventListener("click", openModal);
cancelDeleteBtn.addEventListener("click", closeModal);
deleteModal.addEventListener("click", (e) => {
  if (e.target === deleteModal) closeModal();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && deleteModal.classList.contains("open")) closeModal();
});

deleteConfirmInput.addEventListener("input", () => {
  confirmDeleteBtn.disabled = deleteConfirmInput.value.trim() !== "DELETE";
});

confirmDeleteBtn.addEventListener("click", () => {
  // In production this submits a POST to the account-deletion endpoint.
  closeModal();
  showToast("Account deletion requested");
});
