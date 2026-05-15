/* Fimiku Admin Premium JS */
document.addEventListener("DOMContentLoaded", function () {

  // ── Light / Dark Toggle ──
  const stored = localStorage.getItem("fimiku_admin_theme") || "dark";
  document.documentElement.setAttribute("data-theme", stored);

  const toggle = document.createElement("button");
  toggle.id = "theme-toggle";
  toggle.innerHTML = stored === "dark"
    ? '<span class="material-symbols-outlined">light_mode</span>'
    : '<span class="material-symbols-outlined">dark_mode</span>';
  toggle.title = "Toggle Light/Dark Mode";
  toggle.style.cssText = [
    "position:fixed","bottom:1.5rem","right:1.5rem","z-index:9999",
    "width:44px","height:44px","border-radius:50%",
    "background:#7c3aed","color:#fff","border:none",
    "cursor:pointer","display:flex","align-items:center",
    "justify-content:center","box-shadow:0 4px 16px rgba(124,58,237,.4)",
    "transition:all .2s ease"
  ].join(";");

  toggle.addEventListener("click", function () {
    const current = document.documentElement.getAttribute("data-theme");
    const next    = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("fimiku_admin_theme", next);
    toggle.innerHTML = next === "dark"
      ? '<span class="material-symbols-outlined">light_mode</span>'
      : '<span class="material-symbols-outlined">dark_mode</span>';
  });

  document.body.appendChild(toggle);

  // ── Auto-refresh KPI every 60s ──
  const isIndex = window.location.pathname === "/admin/"
               || window.location.pathname === "/admin/index.html";
  if (isIndex) {
    setTimeout(() => window.location.reload(), 60000);
  }

  // ── Confirm bulk delete with nicer message ──
  const deleteBtn = document.querySelector("input[name='index'][value='0']");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", function (e) {
      if (!confirm("⚠️ Are you sure you want to delete the selected items? This cannot be undone.")) {
        e.preventDefault();
      }
    });
  }

  // ── Add "copied" effect to order IDs ──
  document.querySelectorAll("[style*='monospace']").forEach(el => {
    el.style.cursor = "pointer";
    el.title = "Click to copy";
    el.addEventListener("click", function () {
      navigator.clipboard.writeText(el.textContent.trim()).then(() => {
        const orig = el.textContent;
        el.textContent = "✓ Copied!";
        setTimeout(() => el.textContent = orig, 1500);
      });
    });
  });

  // ── KPI card hover ripple ──
  document.querySelectorAll(".kpi-card").forEach(card => {
    card.addEventListener("mouseenter", function () {
      this.style.boxShadow = "0 12px 32px rgba(124,58,237,.2)";
    });
    card.addEventListener("mouseleave", function () {
      this.style.boxShadow = "";
    });
  });
});
