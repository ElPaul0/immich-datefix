const I18N = {
  en: {
    logout: "Log out",
    auth_title_login: "Sign in",
    auth_title_setup: "Create account",
    auth_hint_login: "Enter your username and PIN — your Immich API key is already linked to the account.",
    auth_hint_setup: "First run: pick a username, a PIN, and attach your Immich API key.",
    auth_legacy: "An existing global key can be replaced by this account’s key.",
    username: "Username",
    pin: "PIN (4–8 digits)",
    pin_short: "PIN",
    immich_url: "Immich URL",
    immich_key: "Immich API key",
    login: "Sign in",
    create_login: "Create & sign in",
    auth_title_register: "Create an account",
    auth_hint_register: "Pick a username, a PIN, and attach an Immich API key.",
    create_account: "Create account",
    switch_to_register: "Add a user",
    switch_to_login: "Already have an account? Sign in",
    account_title: "Account & Immich",
    url: "URL",
    new_api_key: "New API key",
    new_api_key_ph: "leave empty to keep current",
    new_pin: "New PIN",
    optional: "optional",
    save: "Save",
    test: "Test",
    add_user: "Add another user",
    create: "Create",
    scan_title: "Scan",
    scan_hint:
      "Walks the Immich library, detects dates in filenames (WhatsApp, screenshots, timestamps…) and proposes fixes when Immich’s date differs.",
    scan_btn: "Scan library",
    scan_none: "No scan yet.",
    scan_summary: "{scanned} assets · {matched} dated names · {fix} proposed fixes",
    scan_progress: "Scanning… {n}",
    patterns_title: "Detected filename types",
    patterns_hint: "Tick the families to fix, then dry-run or apply.",
    all: "All",
    none: "None",
    dry_run: "Dry-run",
    apply: "Apply fixes",
    ready: "Ready",
    setup: "Setup",
    disconnected: "Signed out",
    scanning: "Scanning…",
    fixing: "Fixing…",
    error: "Error",
    settings_ok: "Settings saved",
    user_created: "User created",
    user_created_alert: "Account created. You can sign out and sign back in with that account.",
    pick_pattern: "Select at least one filename type",
    confirm_apply: "Fix dates for {n} filename type(s)?",
    dry_ok: "Dry-run OK",
    fixed: "Fixed {n}",
    connected_key: "Signed in · {user} · key {hint} · min delta {hours}h",
    connected_nokey: "Signed in · {user} · no API key",
    to_fix: "{n} to fix",
    matched: "{n} matched",
    pat_whatsapp: "IMG-/VID-YYYYMMDD-WA#### — date is often receive time",
    pat_screenshot: "Screenshot_YYYYMMDD-HHMMSS",
    pat_pixel: "PXL_YYYYMMDD_HHMMSS…",
    pat_img_underscore: "Common camera / export naming",
    pat_yyyymmdd_hhmmss: "Compact date-time prefix",
    pat_iso_filename: "ISO-ish date in the filename",
    pat_unix_ms: "13 digits (Unix epoch milliseconds)",
    pat_unix_s: "10 digits (Unix epoch seconds)",
    pat_dotnet_ticks: "~18 digits (.NET / Facebook-like ticks)",
  },
  fr: {
    logout: "Déconnexion",
    auth_title_login: "Connexion",
    auth_title_setup: "Créer un compte",
    auth_hint_login: "Entre ton identifiant et ton code PIN — la clé Immich est déjà liée à ton compte.",
    auth_hint_setup: "Premier démarrage : choisis un identifiant, un PIN, et associe ta clé API Immich.",
    auth_legacy: "Une clé globale existante pourra être remplacée par celle du compte.",
    username: "Identifiant",
    pin: "PIN (4–8 chiffres)",
    pin_short: "PIN",
    immich_url: "URL Immich",
    immich_key: "Clé API Immich",
    login: "Se connecter",
    create_login: "Créer et se connecter",
    auth_title_register: "Créer un compte",
    auth_hint_register: "Choisis un identifiant, un PIN, et associe une clé API Immich.",
    create_account: "Créer le compte",
    switch_to_register: "Ajouter un utilisateur",
    switch_to_login: "Déjà un compte ? Se connecter",
    account_title: "Compte & Immich",
    url: "URL",
    new_api_key: "Nouvelle clé API",
    new_api_key_ph: "laisser vide pour garder l’actuelle",
    new_pin: "Nouveau PIN",
    optional: "optionnel",
    save: "Enregistrer",
    test: "Tester",
    add_user: "Ajouter un autre utilisateur",
    create: "Créer",
    scan_title: "Scan",
    scan_hint:
      "Parcourt la bibliothèque Immich, détecte les dates dans les noms de fichiers (WhatsApp, screenshots, timestamps…) et propose les corrections quand la date Immich diffère.",
    scan_btn: "Scanner la bibliothèque",
    scan_none: "Pas encore de scan.",
    scan_summary: "{scanned} assets · {matched} noms datés · {fix} corrections proposées",
    scan_progress: "Scan… {n}",
    patterns_title: "Types de noms détectés",
    patterns_hint: "Coche les familles à corriger, puis dry-run ou appliquer.",
    all: "Tout",
    none: "Aucun",
    dry_run: "Dry-run",
    apply: "Appliquer les corrections",
    ready: "Prêt",
    setup: "Setup",
    disconnected: "Déconnecté",
    scanning: "Scan…",
    fixing: "Correction…",
    error: "Erreur",
    settings_ok: "Réglages OK",
    user_created: "Utilisateur créé",
    user_created_alert: "Compte créé. Tu peux te déconnecter puis te reconnecter avec ce compte.",
    pick_pattern: "Coche au moins un type de nom",
    confirm_apply: "Corriger les dates pour {n} type(s) de noms ?",
    dry_ok: "Dry-run OK",
    fixed: "Corrigé {n}",
    connected_key: "Connecté · {user} · clé {hint} · écart min {hours}h",
    connected_nokey: "Connecté · {user} · aucune clé API",
    to_fix: "{n} à corriger",
    matched: "{n} matchés",
    pat_whatsapp: "IMG-/VID-YYYYMMDD-WA#### — date souvent = réception",
    pat_screenshot: "Screenshot_YYYYMMDD-HHMMSS",
    pat_pixel: "PXL_YYYYMMDD_HHMMSS…",
    pat_img_underscore: "Classique appareil / export",
    pat_yyyymmdd_hhmmss: "Préfixe date-heure compact",
    pat_iso_filename: "ISO-ish dans le nom",
    pat_unix_ms: "13 chiffres (epoch millisecondes)",
    pat_unix_s: "10 chiffres (epoch secondes)",
    pat_dotnet_ticks: "~18 chiffres (ticks 100ns depuis year 1)",
  },
};

const PAT_DESC_KEY = {
  whatsapp: "pat_whatsapp",
  screenshot: "pat_screenshot",
  pixel: "pat_pixel",
  img_underscore: "pat_img_underscore",
  yyyymmdd_hhmmss: "pat_yyyymmdd_hhmmss",
  iso_filename: "pat_iso_filename",
  unix_ms: "pat_unix_ms",
  unix_s: "pat_unix_s",
  dotnet_ticks: "pat_dotnet_ticks",
};

const statusBadge = document.getElementById("status-badge");
const authPanel = document.getElementById("auth-panel");
const appRoot = document.getElementById("app-root");
const userChip = document.getElementById("user-chip");
const btnLogout = document.getElementById("btn-logout");
const authTitle = document.getElementById("auth-title");
const authHint = document.getElementById("auth-hint");
const authMeta = document.getElementById("auth-meta");
const setupFields = document.getElementById("setup-fields");
const btnAuth = document.getElementById("btn-auth");
const immichUrl = document.getElementById("immich-url");
const immichKey = document.getElementById("immich-key");
const newPin = document.getElementById("new-pin");
const settingsMeta = document.getElementById("settings-meta");
const scanMeta = document.getElementById("scan-meta");
const patternsSection = document.getElementById("patterns-section");
const patternList = document.getElementById("pattern-list");
const applyOut = document.getElementById("apply-out");
const progressWrap = document.getElementById("progress-wrap");
const progressBar = document.getElementById("progress-bar");
const progressLabel = document.getElementById("progress-label");
const progressPct = document.getElementById("progress-pct");
const btnScan = document.getElementById("btn-scan");
const btnDry = document.getElementById("btn-dry");
const btnApply = document.getElementById("btn-apply");

let pollTimer = null;
let lastPatterns = [];
let authMode = "login";
let authDefaults = {};
let lang = localStorage.getItem("datefix_lang") || "en";
let theme = localStorage.getItem("datefix_theme") || "dark";
let sessionScanActive = false; // only show scan UI for this page session

function t(key, vars = {}) {
  const table = I18N[lang] || I18N.en;
  let s = table[key] ?? I18N.en[key] ?? key;
  Object.entries(vars).forEach(([k, v]) => {
    s = s.replaceAll(`{${k}}`, String(v));
  });
  return s;
}

function applyTheme() {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("datefix_theme", theme);
  document.getElementById("btn-theme-dark").classList.toggle("is-active", theme === "dark");
  document.getElementById("btn-theme-light").classList.toggle("is-active", theme === "light");
}

function applyLang() {
  document.documentElement.setAttribute("lang", lang);
  localStorage.setItem("datefix_lang", lang);
  document.getElementById("btn-lang-fr").classList.toggle("is-active", lang === "fr");
  document.getElementById("btn-lang-en").classList.toggle("is-active", lang === "en");

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (!key) return;
    if (el.id === "auth-title" || el.id === "auth-hint" || el.id === "btn-auth" || el.id === "btn-auth-switch") return;
    if (el.id === "scan-meta" && sessionScanActive) return;
    el.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.setAttribute("placeholder", t(el.getAttribute("data-i18n-placeholder")));
  });

  // Re-apply auth mode strings
  if (!authPanel.classList.contains("hidden")) {
    paintAuthCopy();
  }
  if (lastPatterns.length && sessionScanActive) {
    renderPatterns(lastPatterns);
  }
  if (!sessionScanActive && scanMeta) {
    scanMeta.textContent = t("scan_none");
  }
}

function paintAuthCopy() {
  const switchBtn = document.getElementById("btn-auth-switch");
  const switchRow = document.getElementById("auth-switch-row");
  if (authMode === "setup") {
    authTitle.textContent = t("auth_title_setup");
    authHint.textContent = t("auth_hint_setup");
    btnAuth.textContent = t("create_login");
    switchRow.classList.add("hidden");
  } else if (authMode === "register") {
    authTitle.textContent = t("auth_title_register");
    authHint.textContent = t("auth_hint_register");
    btnAuth.textContent = t("create_account");
    switchBtn.textContent = t("switch_to_login");
    switchRow.classList.remove("hidden");
  } else {
    authTitle.textContent = t("auth_title_login");
    authHint.textContent = t("auth_hint_login");
    btnAuth.textContent = t("login");
    switchBtn.textContent = t("switch_to_register");
    switchRow.classList.remove("hidden");
  }
}

async function api(path, opts = {}) {
  const res = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = j.detail || JSON.stringify(j);
    } catch (_) {}
    const err = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    err.status = res.status;
    throw err;
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res;
}

function setBadge(text, cls) {
  statusBadge.textContent = text;
  statusBadge.classList.remove("ok", "err");
  if (cls) statusBadge.classList.add(cls);
}

function setBusy(busy) {
  btnScan.disabled = busy;
  btnDry.disabled = busy;
  btnApply.disabled = busy;
}

function clearScanUi(messageKey = "scan_none") {
  sessionScanActive = false;
  lastPatterns = [];
  patternsSection.classList.add("hidden");
  patternList.innerHTML = "";
  applyOut.classList.add("hidden");
  applyOut.textContent = "";
  progressWrap.classList.add("hidden");
  scanMeta.textContent = t(messageKey);
}

function showAuth(mode, defaults = {}) {
  authMode = mode;
  authDefaults = defaults;
  authPanel.classList.remove("hidden");
  appRoot.classList.add("hidden");
  userChip.classList.add("hidden");
  btnLogout.classList.add("hidden");
  setupFields.classList.toggle("hidden", mode === "login");
  paintAuthCopy();
  if (mode === "setup" || mode === "register") {
    const urlInput = document.getElementById("setup-url");
    if (!urlInput.value) urlInput.value = defaults.immich_url || "";
    authMeta.textContent = mode === "setup" && defaults.has_legacy_key ? t("auth_legacy") : "";
  } else {
    authMeta.textContent = "";
  }
  setBadge(mode === "setup" ? t("setup") : t("disconnected"));
}

function showApp(user) {
  authPanel.classList.add("hidden");
  appRoot.classList.remove("hidden");
  userChip.classList.remove("hidden");
  btnLogout.classList.remove("hidden");
  userChip.textContent = user?.username || "";
  setBadge(t("ready"), "ok");
}

function updateProgress(st) {
  const running = st.state === "running";
  if (!running && st.state !== "done") {
    if (st.state === "error") progressWrap.classList.add("hidden");
    if (!running) return;
  }
  if (st.state === "error") {
    progressWrap.classList.add("hidden");
    return;
  }

  progressWrap.classList.remove("hidden");
  progressLabel.textContent = st.message || "…";
  const known = st.total > 0;
  progressBar.classList.toggle("indeterminate", running && !known);
  if (known) {
    const pct = Math.max(0, Math.min(100, st.percent || 0));
    progressBar.style.width = `${pct}%`;
    progressPct.textContent = `${pct}% · ${st.done}/${st.total}`;
  } else {
    progressBar.style.width = "35%";
    progressPct.textContent = `${st.done || 0}…`;
  }
  if (st.state === "done") {
    progressBar.classList.remove("indeterminate");
    progressBar.style.width = "100%";
    progressPct.textContent = st.total ? `100% · ${st.done}/${st.total}` : "OK";
  }
}

async function loadSettings() {
  const s = await api("/api/settings");
  immichUrl.value = s.immich_url || "";
  settingsMeta.textContent = s.has_api_key
    ? t("connected_key", {
        user: s.username,
        hint: s.api_key_hint,
        hours: Math.round(s.min_delta_seconds / 3600),
      })
    : t("connected_nokey", { user: s.username });
}

async function boot() {
  clearScanUi();
  const st = await api("/api/auth/status");
  if (st.needs_setup) {
    showAuth("setup", {
      immich_url: st.default_immich_url,
      has_legacy_key: st.has_legacy_key,
    });
    return;
  }
  if (!st.authenticated) {
    showAuth("login", { immich_url: st.default_immich_url });
    return;
  }
  showApp(st.user);
  await loadSettings();
  // Drop any previous scan stored on the server so refresh starts clean
  try {
    await api("/api/job/clear", { method: "POST", body: "{}" });
  } catch (_) {}
  // Resume only if a job is currently running in this browser session start
  const job = await api("/api/job");
  if (job.state === "running") {
    sessionScanActive = true;
    await startPolling();
  }
}

btnAuth.addEventListener("click", async () => {
  const username = document.getElementById("auth-user").value.trim();
  const pin = document.getElementById("auth-pin").value.trim();
  try {
    if (authMode === "setup" || authMode === "register") {
      await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          username,
          pin,
          immich_url: document.getElementById("setup-url").value.trim() || undefined,
          immich_api_key: document.getElementById("setup-key").value.trim(),
        }),
      });
    } else {
      await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, pin }),
      });
    }
    document.getElementById("auth-pin").value = "";
    document.getElementById("setup-key").value = "";
    await boot();
  } catch (e) {
    authMeta.textContent = e.message;
    setBadge(t("error"), "err");
  }
});

document.getElementById("btn-auth-switch").addEventListener("click", () => {
  const next = authMode === "register" ? "login" : "register";
  showAuth(next, authDefaults);
});

btnLogout.addEventListener("click", async () => {
  try {
    await api("/api/auth/logout", { method: "POST", body: "{}" });
  } catch (_) {}
  stopPoll();
  clearScanUi();
  await boot();
});

document.getElementById("btn-save").addEventListener("click", async () => {
  try {
    await api("/api/settings", {
      method: "POST",
      body: JSON.stringify({
        immich_url: immichUrl.value.trim(),
        immich_api_key: immichKey.value.trim() || undefined,
        pin: newPin.value.trim() || undefined,
      }),
    });
    immichKey.value = "";
    newPin.value = "";
    await loadSettings();
    setBadge(t("settings_ok"), "ok");
  } catch (e) {
    alert(e.message);
  }
});

document.getElementById("btn-add-user").addEventListener("click", async () => {
  try {
    await api("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        username: document.getElementById("new-user").value.trim(),
        pin: document.getElementById("new-user-pin").value.trim(),
        immich_api_key: document.getElementById("new-user-key").value.trim(),
        immich_url: immichUrl.value.trim() || undefined,
      }),
    });
    document.getElementById("new-user").value = "";
    document.getElementById("new-user-pin").value = "";
    document.getElementById("new-user-key").value = "";
    setBadge(t("user_created"), "ok");
    alert(t("user_created_alert"));
  } catch (e) {
    alert(e.message);
  }
});

document.getElementById("btn-ping").addEventListener("click", async () => {
  try {
    const r = await api("/api/ping", { method: "POST", body: "{}" });
    setBadge(`Immich ${r.version.major}.${r.version.minor}.${r.version.patch}`, "ok");
  } catch (e) {
    setBadge("Ping KO", "err");
    alert(e.message);
  }
});

function selectedIds() {
  return [...patternList.querySelectorAll("input.pat-cb:checked")].map((cb) => cb.dataset.id);
}

function patternDesc(p) {
  const key = PAT_DESC_KEY[p.id];
  return key ? t(key) : p.description;
}

function renderPatterns(patterns) {
  lastPatterns = patterns || [];
  patternList.innerHTML = "";
  if (!lastPatterns.length) {
    patternsSection.classList.add("hidden");
    return;
  }
  patternsSection.classList.remove("hidden");
  lastPatterns.forEach((p) => {
    const row = document.createElement("label");
    row.className = "pattern-row" + (p.needs_fix > 0 ? " is-on" : "");
    const samples = (p.samples || [])
      .slice(0, 3)
      .map(
        (s) =>
          `${s.filename}: ${(s.current_date || "∅").slice(0, 10)} → ${s.name_date.slice(0, 10)}`
      )
      .join(" · ");
    row.innerHTML = `
      <input type="checkbox" class="pat-cb" data-id="${p.id}" ${p.needs_fix ? "checked" : ""}>
      <div>
        <div class="title">${p.label}</div>
        <div class="desc">${patternDesc(p)}</div>
        <div class="ex">${p.example}</div>
        ${samples ? `<div class="samples">${samples}</div>` : ""}
      </div>
      <div class="stats">
        <div class="fix">${t("to_fix", { n: p.needs_fix })}</div>
        <div>${t("matched", { n: p.matched })}</div>
      </div>
    `;
    patternList.appendChild(row);
  });
}

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

async function pollJob() {
  try {
    const st = await api("/api/job");
    updateProgress(st);

    if (st.state === "running") {
      setBusy(true);
      setBadge(st.kind === "apply" ? t("fixing") : t("scanning"), "ok");
      if (st.kind === "scan") {
        scanMeta.textContent = t("scan_progress", { n: st.done || 0 });
      }
      return;
    }

    stopPoll();
    setBusy(false);

    if (st.state === "error") {
      setBadge(t("error"), "err");
      scanMeta.textContent = st.error || st.message;
      applyOut.classList.remove("hidden");
      applyOut.textContent = st.error || st.message;
      return;
    }

    setBadge(t("ready"), "ok");

    // Real apply (not dry-run): clear scan so user must re-scan to verify
    if (st.kind === "apply" && st.result && !st.result.dry_run) {
      const resultJson = JSON.stringify(st.result, null, 2);
      const updated = st.result.updated;
      clearScanUi("scan_none");
      applyOut.classList.remove("hidden");
      applyOut.textContent = resultJson;
      setBadge(t("fixed", { n: updated }), "ok");
      return;
    }

    if (st.kind === "apply" && st.result && st.result.dry_run) {
      applyOut.classList.remove("hidden");
      applyOut.textContent = JSON.stringify(st.result, null, 2);
      setBadge(t("dry_ok"), "ok");
    }

    if (sessionScanActive && st.summary) {
      scanMeta.textContent = t("scan_summary", {
        scanned: st.summary.scanned,
        matched: st.summary.matched_any,
        fix: st.summary.needs_fix,
      });
      renderPatterns(st.summary.patterns);
    }
  } catch (e) {
    if (e.status === 401) {
      stopPoll();
      showAuth("login");
      return;
    }
    throw e;
  }
}

function startPolling() {
  stopPoll();
  pollTimer = setInterval(pollJob, 500);
  return pollJob();
}

document.getElementById("btn-scan").addEventListener("click", async () => {
  try {
    clearScanUi();
    sessionScanActive = true;
    await api("/api/scan", { method: "POST", body: "{}" });
    await startPolling();
  } catch (e) {
    sessionScanActive = false;
    alert(e.message);
  }
});

document.getElementById("btn-all").addEventListener("click", () => {
  patternList.querySelectorAll("input.pat-cb").forEach((cb) => {
    cb.checked = true;
  });
});
document.getElementById("btn-none").addEventListener("click", () => {
  patternList.querySelectorAll("input.pat-cb").forEach((cb) => {
    cb.checked = false;
  });
});

async function doApply(dry) {
  const ids = selectedIds();
  if (!ids.length) {
    alert(t("pick_pattern"));
    return;
  }
  if (!dry && !confirm(t("confirm_apply", { n: ids.length }))) return;
  try {
    applyOut.classList.add("hidden");
    await api("/api/apply", {
      method: "POST",
      body: JSON.stringify({ pattern_ids: ids, dry_run: dry }),
    });
    await startPolling();
  } catch (e) {
    alert(e.message);
  }
}

document.getElementById("btn-dry").addEventListener("click", () => doApply(true));
document.getElementById("btn-apply").addEventListener("click", () => doApply(false));

document.querySelectorAll("[data-theme-set]").forEach((btn) => {
  btn.addEventListener("click", () => {
    theme = btn.getAttribute("data-theme-set");
    applyTheme();
  });
});
document.querySelectorAll("[data-lang-set]").forEach((btn) => {
  btn.addEventListener("click", () => {
    lang = btn.getAttribute("data-lang-set");
    applyLang();
  });
});

["auth-user", "auth-pin", "setup-key"].forEach((id) => {
  document.getElementById(id).addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") btnAuth.click();
  });
});

applyTheme();
applyLang();
boot().catch((e) => {
  console.error(e);
  setBadge(t("error"), "err");
  authMeta.textContent = e.message || String(e);
});
