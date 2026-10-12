const statusBadge = document.getElementById("status-badge");
const authPanel = document.getElementById("auth-panel");
const appRoot = document.getElementById("app-root");
const headerUser = document.getElementById("header-user");
const userChip = document.getElementById("user-chip");
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
let authMode = "login"; // login | setup

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

function showAuth(mode, defaults = {}) {
  authMode = mode;
  authPanel.classList.remove("hidden");
  appRoot.classList.add("hidden");
  headerUser.classList.add("hidden");
  setupFields.classList.toggle("hidden", mode !== "setup");
  if (mode === "setup") {
    authTitle.textContent = "Créer un compte";
    authHint.textContent =
      "Premier démarrage : choisis un identifiant, un PIN, et associe ta clé API Immich.";
    btnAuth.textContent = "Créer et se connecter";
    document.getElementById("setup-url").value = defaults.immich_url || "";
    if (defaults.has_legacy_key) {
      authMeta.textContent = "Une clé globale existante pourra être remplacée par celle du compte.";
    }
  } else {
    authTitle.textContent = "Connexion";
    authHint.textContent =
      "Entre ton identifiant et ton code PIN — la clé Immich est déjà liée à ton compte.";
    btnAuth.textContent = "Se connecter";
    authMeta.textContent = "";
  }
  setBadge(mode === "setup" ? "Setup" : "Déconnecté");
}

function showApp(user) {
  authPanel.classList.add("hidden");
  appRoot.classList.remove("hidden");
  headerUser.classList.remove("hidden");
  userChip.textContent = user?.username || "";
  setBadge("Prêt", "ok");
}

function updateProgress(st) {
  const running = st.state === "running";
  progressWrap.classList.toggle("hidden", !running && st.state !== "done");
  if (!running && st.state !== "done" && st.state !== "error") {
    progressWrap.classList.add("hidden");
    return;
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
    ? `Connecté · ${s.username} · clé ${s.api_key_hint} · écart min ${Math.round(s.min_delta_seconds / 3600)}h`
    : `Connecté · ${s.username} · aucune clé API`;
}

async function boot() {
  const st = await api("/api/auth/status");
  if (st.needs_setup) {
    showAuth("setup", {
      immich_url: st.default_immich_url,
      has_legacy_key: st.has_legacy_key,
    });
    return;
  }
  if (!st.authenticated) {
    showAuth("login");
    return;
  }
  showApp(st.user);
  await loadSettings();
  await pollJob();
}

btnAuth.addEventListener("click", async () => {
  const username = document.getElementById("auth-user").value.trim();
  const pin = document.getElementById("auth-pin").value.trim();
  try {
    if (authMode === "setup") {
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
    setBadge("Erreur", "err");
  }
});

document.getElementById("btn-logout").addEventListener("click", async () => {
  try {
    await api("/api/auth/logout", { method: "POST", body: "{}" });
  } catch (_) {}
  stopPoll();
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
    setBadge("Réglages OK", "ok");
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
    setBadge("Utilisateur créé", "ok");
    alert("Compte créé. Tu peux te déconnecter puis te reconnecter avec ce compte.");
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
        <div class="desc">${p.description}</div>
        <div class="ex">${p.example}</div>
        ${samples ? `<div class="samples">${samples}</div>` : ""}
      </div>
      <div class="stats">
        <div class="fix">${p.needs_fix} à corriger</div>
        <div>${p.matched} matchés</div>
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
      setBadge(st.kind === "apply" ? "Correction…" : "Scan…", "ok");
      if (st.kind === "scan") {
        scanMeta.textContent = st.message || `Scan… ${st.done}`;
      }
      return;
    }

    stopPoll();
    setBusy(false);

    if (st.state === "error") {
      setBadge("Erreur", "err");
      scanMeta.textContent = st.error || st.message;
      applyOut.classList.remove("hidden");
      applyOut.textContent = st.error || st.message;
      return;
    }

    setBadge("Prêt", "ok");
    if (st.summary) {
      scanMeta.textContent =
        `${st.summary.scanned} assets · ${st.summary.matched_any} noms datés · ` +
        `${st.summary.needs_fix} corrections proposées`;
      renderPatterns(st.summary.patterns);
    }
    if (st.kind === "apply" && st.result) {
      applyOut.classList.remove("hidden");
      applyOut.textContent = JSON.stringify(st.result, null, 2);
      setBadge(
        st.result.dry_run ? "Dry-run OK" : `Corrigé ${st.result.updated}`,
        "ok"
      );
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
    await api("/api/scan", { method: "POST", body: "{}" });
    await startPolling();
  } catch (e) {
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
    alert("Coche au moins un type de nom");
    return;
  }
  if (!dry && !confirm(`Corriger les dates pour ${ids.length} type(s) de noms ?`)) return;
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

["auth-user", "auth-pin", "setup-key"].forEach((id) => {
  document.getElementById(id).addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") btnAuth.click();
  });
});

boot().catch((e) => {
  console.error(e);
  setBadge("Erreur", "err");
  authMeta.textContent = e.message || String(e);
});
