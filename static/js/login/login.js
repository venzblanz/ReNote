// ---- password visibility toggle ----
const pwInput = document.getElementById("id_password");
const togglePw = document.getElementById("togglePw");

togglePw.addEventListener("click", () => {
  const isPassword = pwInput.type === "password";
  pwInput.type = isPassword ? "text" : "password";
  togglePw.setAttribute("aria-pressed", isPassword);
  togglePw.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
});

// ---- lightweight client-side validation ----
const form = document.querySelector(".auth-card form");
const card = document.querySelector(".auth-card");
const usernameInput = document.getElementById("id_username");

form.addEventListener("submit", (e) => {
  const missing = [usernameInput, pwInput].filter((input) => !input.value.trim());

  if (missing.length) {
    e.preventDefault();
    missing.forEach((input) => input.classList.add("invalid"));
    card.classList.remove("shake");
    void card.offsetWidth; // restart animation
    card.classList.add("shake");
    missing[0].focus();
  }
});

[usernameInput, pwInput].forEach((input) => {
  input.addEventListener("input", () => input.classList.remove("invalid"));
});
