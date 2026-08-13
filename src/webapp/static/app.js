(() => {
  const crcCheck = document.getElementById("crc-check");
  const libraryForm = document.getElementById("library-form");
  const libraryMsg = document.getElementById("library-msg");
  const processForm = document.getElementById("process-form");
  const processBtn = document.getElementById("process-btn");
  const redumpRename = document.getElementById("redump-rename");
  const summaryEl = document.getElementById("summary");
  const tbody = document.querySelector("#games-table tbody");
  const statusBox = document.getElementById("status");
  const statusBar = document.getElementById("status-bar");
  const statusText = document.getElementById("status-text");
  const errorList = document.getElementById("error-list");

  let pollTimer = null;

  function setMsg(text, kind) {
    libraryMsg.textContent = text || "";
    libraryMsg.className = "msg" + (kind ? ` ${kind}` : "");
  }

  function cu2Label(g) {
    if (!g.cu2_required) return "*";
    return g.cu2_present ? "Yes" : "No";
  }

  function lstLabel(g) {
    if (!g.multi_disc) return "*";
    return g.lst_present ? "Yes" : "No";
  }

  function libcryptLabel(g) {
    if (!g.libcrypt_required) return "*";
    return g.libcrypt_applied ? "Yes" : "No";
  }

  function crcLabel(g) {
    // Match Tk/README: * = check off; Yes/No = result; — = no Redump track data
    if (!g.crc_checked) return "*";
    if (g.crc_valid === true) return "Yes";
    if (g.crc_valid === false) return "No";
    return "—";
  }

  function renderSummary(summary) {
    if (!summary) {
      summaryEl.innerHTML = '<p class="muted">Scan a library to see counts.</p>';
      return;
    }
    const rows = [
      ["Total", summary.total_games],
      ["Unidentified", summary.unidentified],
      ["No cover", summary.without_cover],
      ["Multi-bin", summary.multi_bin],
      ["Invalid names", summary.invalid_names],
      ["Multi-disc games", summary.multi_disc_games],
    ];
    summaryEl.innerHTML = rows
      .map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`)
      .join("");
  }

  function renderGames(games) {
    if (!games || !games.length) {
      tbody.innerHTML = '<tr class="empty"><td colspan="9">No games loaded.</td></tr>';
      processBtn.disabled = true;
      return;
    }
    processBtn.disabled = false;
    tbody.innerHTML = games
      .map(
        (g) => `<tr>
          <td>${escapeHtml(g.name)}</td>
          <td>${escapeHtml(g.id || "—")}</td>
          <td>${g.disc_number}</td>
          <td>${g.bin_count}</td>
          <td>${g.cover_art ? "Yes" : "No"}</td>
          <td>${cu2Label(g)}</td>
          <td>${lstLabel(g)}</td>
          <td>${libcryptLabel(g)}</td>
          <td>${crcLabel(g)}</td>
        </tr>`
      )
      .join("");
  }

  function renderErrors(errors) {
    if (!errors || !errors.length) {
      errorList.hidden = true;
      errorList.innerHTML = "";
      return;
    }
    errorList.hidden = false;
    errorList.innerHTML = errors
      .map((e) => `<li><strong>${escapeHtml(e.name)}</strong>: ${escapeHtml(e.error)}</li>`)
      .join("");
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || `Request failed (${res.status})`);
    }
    return data;
  }

  libraryForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMsg("Scanning…");
    processBtn.disabled = true;
    renderErrors([]);
    try {
      const data = await postJson("/api/library", {
        crc_check: crcCheck.checked,
      });
      renderSummary(data.summary);
      renderGames(data.games);
      setMsg(`Loaded ${data.games.length} game(s).`, "ok");
    } catch (err) {
      setMsg(err.message, "error");
      processBtn.disabled = true;
    }
  });

  function showStatus(status) {
    statusBox.hidden = false;
    statusBar.style.width = `${Math.max(0, Math.min(100, status.percent || 0))}%`;
    const errCount = (status.errors && status.errors.length) || 0;
    let line = status.message || status.state || "";
    if (status.state === "completed" && errCount) {
      line += ` (${errCount} error(s))`;
    }
    if (status.state === "failed") {
      line = status.message || "Failed";
    }
    statusText.textContent = line;
  }

  async function pollStatus() {
    try {
      const res = await fetch("/api/process/status");
      const status = await res.json();
      showStatus(status);
      if (status.done) {
        clearInterval(pollTimer);
        pollTimer = null;
        processBtn.disabled = false;
        const gamesRes = await fetch("/api/games");
        const gamesData = await gamesRes.json();
        renderGames(gamesData.games || []);
        renderSummary(gamesData.summary);
        renderErrors(status.errors || []);
        if (status.state === "completed") {
          setMsg("Processing finished.", status.errors?.length ? "error" : "ok");
        } else if (status.state === "failed") {
          setMsg(status.message || "Processing failed.", "error");
        }
      }
    } catch (err) {
      clearInterval(pollTimer);
      pollTimer = null;
      processBtn.disabled = false;
      setMsg(err.message, "error");
    }
  }

  processForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMsg("");
    renderErrors([]);
    processBtn.disabled = true;
    try {
      await postJson("/api/process", {
        redump_rename: redumpRename.checked,
      });
      showStatus({ percent: 0, message: "Starting…", state: "running", done: false });
      if (pollTimer) clearInterval(pollTimer);
      pollTimer = setInterval(pollStatus, 500);
      pollStatus();
    } catch (err) {
      processBtn.disabled = false;
      setMsg(err.message, "error");
    }
  });

  const aboutBtn = document.getElementById("about-btn");
  const aboutDialog = document.getElementById("about-dialog");
  if (aboutBtn && aboutDialog) {
    aboutBtn.addEventListener("click", () => {
      aboutDialog.showModal();
    });
  }
})();
