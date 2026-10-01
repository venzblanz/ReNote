// ---- password visibility toggles ----
document.querySelectorAll(".toggle-pw").forEach((btn) => {
  const target = document.getElementById(btn.dataset.target);
  btn.addEventListener("click", () => {
    const isPassword = target.type === "password";
    target.type = isPassword ? "text" : "password";
    btn.setAttribute("aria-pressed", isPassword);
    btn.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
  });
});

// ---- password strength meter ----
const pw1 = document.getElementById("id_password1");
const pw2 = document.getElementById("id_password2");
const strengthBar = document.querySelector(".strength-bar span");
const strengthLabel = document.getElementById("strengthLabel");
const matchHint = document.getElementById("matchHint");

const levels = [
  { min: 0, width: "8%",   color: "#f87171", label: "Too short" },
  { min: 1, width: "35%",  color: "#f87171", label: "Weak" },
  { min: 2, width: "60%",  color: "#fbbf24", label: "Getting there" },
  { min: 3, width: "82%",  color: "#8b5cf6", label: "Binge-ready" },
  { min: 4, width: "100%", color: "#4ade80", label: "Marathon-proof" },
];

function scorePassword(value) {
  let score = 0;
  if (value.length >= 8) score++;
  if (value.length >= 12) score++;
  if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score++;
  if (/[0-9]/.test(value)) score++;
  if (/[^A-Za-z0-9]/.test(value)) score++;
  return value.length === 0 ? -1 : Math.min(score, 4);
}

pw1.addEventListener("input", () => {
  const score = scorePassword(pw1.value);
  if (score === -1) {
    strengthBar.style.width = "0%";
    strengthLabel.textContent = "\u00A0";
  } else {
    const level = levels[score];
    strengthBar.style.width = level.width;
    strengthBar.style.background = level.color;
    strengthLabel.textContent = level.label;
  }
  checkMatch();
});

function checkMatch() {
  if (!pw2.value) {
    matchHint.textContent = "\u00A0";
    matchHint.className = "field-hint";
    return;
  }
  const matches = pw1.value === pw2.value;
  matchHint.textContent = matches ? "Passwords match" : "Passwords don't match yet";
  matchHint.className = "field-hint " + (matches ? "ok" : "bad");
}
pw2.addEventListener("input", checkMatch);

// ---- form validation ----
const form = document.querySelector(".auth-card form");
const card = document.querySelector(".auth-card");
const requiredFields = [
  document.getElementById("id_username"),
  document.getElementById("id_email"),
  pw1,
  pw2,
];

form.addEventListener("submit", (e) => {
  let blocked = false;
  const missing = requiredFields.filter((input) => !input.value.trim());

  missing.forEach((input) => input.classList.add("invalid"));
  if (missing.length) blocked = true;

  if (pw1.value && pw2.value && pw1.value !== pw2.value) {
    pw2.classList.add("invalid");
    checkMatch();
    blocked = true;
  }

  const terms = form.querySelector('input[name="terms"]');
  if (!terms.checked) blocked = true;

  if (blocked) {
    e.preventDefault();
    card.classList.remove("shake");
    void card.offsetWidth;
    card.classList.add("shake");
    if (missing[0]) missing[0].focus();
  }
});

requiredFields.forEach((input) => {
  input.addEventListener("input", () => input.classList.remove("invalid"));
});
