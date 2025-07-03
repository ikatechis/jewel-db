/* items_list.js --------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  /* ---------- constants ---------- */
  const VIEW_KEY = "itemsListView";            // localStorage key

  /* ---------- DOM refs ---------- */
  const deleteSelectedBtn = document.getElementById("delete-selected");
  const selectAllBtn      = document.getElementById("select-all");
  const gridViewBtn       = document.getElementById("gridView");
  const listViewBtn       = document.getElementById("listView");
  const gridEl            = document.getElementById("grid");
  const listEl            = document.getElementById("list");

  const getItemChecks = () =>
    Array.from(document.querySelectorAll(".select-item"));

  /* ---------- restore saved view ---------- */
  (function applySavedView() {
    const saved = localStorage.getItem(VIEW_KEY) || "grid";
    if (saved === "list") {
      listEl.classList.remove("hidden");
      gridEl.classList.add("hidden");
    } else {
      gridEl.classList.remove("hidden");
      listEl.classList.add("hidden");
    }
  })();

  /* ---------- batch-button visibility ---------- */
  const updateBatchBtn = () => {
    const anyChecked = getItemChecks().some((cb) => cb.checked);
    deleteSelectedBtn.classList.toggle("hidden", !anyChecked);
  };

  getItemChecks().forEach((cb) =>
    cb.addEventListener("change", updateBatchBtn)
  );

  if (selectAllBtn) {
    selectAllBtn.addEventListener("change", () => {
      const checked = selectAllBtn.checked;
      getItemChecks().forEach((cb) => (cb.checked = checked));
      updateBatchBtn();
    });
  }

  updateBatchBtn(); // initial

  /* ---------- batch delete ---------- */
  deleteSelectedBtn.addEventListener("click", async () => {
    const ids = getItemChecks()
      .filter((cb) => cb.checked)
      .map((cb) => Number(cb.value));

    if (!ids.length) {
      alert("No items selected");
      return;
    }
    if (!confirm(`Delete ${ids.length} selected item(s)?`)) return;

    const res = await fetch("/api/items/batch", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids }),
    });
    if (res.ok) window.location.reload();
    else        alert("Batch delete failed");
  });

  /* ---------- single delete ---------- */
  document.querySelectorAll(".delete-item").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this item?")) return;
      const id = btn.dataset.id;
      const r  = await fetch(`/api/items/${id}`, { method: "DELETE" });
      if (r.status === 204) window.location.reload();
      else                  alert("Delete failed");
    });
  });

  /* ---------- grid / list toggle ---------- */
  gridViewBtn?.addEventListener("click", () => {
    gridEl.classList.remove("hidden");
    listEl.classList.add("hidden");
    localStorage.setItem(VIEW_KEY, "grid");
  });

  listViewBtn?.addEventListener("click", () => {
    listEl.classList.remove("hidden");
    gridEl.classList.add("hidden");
    localStorage.setItem(VIEW_KEY, "list");
  });
});
