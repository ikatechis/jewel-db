// jewel_db/static/js/main.js

console.log("main.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  // ————————————————
  // 1) FORM SUBMIT HANDLER
  // ————————————————
  const form = document.getElementById("item-form");
  if (form) {
    const submitBtn = form.querySelector('button[type="submit"]');

    async function handleSubmit(e) {
      e.preventDefault();
      submitBtn.disabled = true;

      // Gather fields (excluding files)
      const fd = new FormData(form);
      const data = Object.fromEntries(
        Array.from(fd.entries()).filter(([k]) => k !== "files")
      );

      // Create or update
      const method = data.id ? "PATCH" : "POST";
      const url    = data.id ? `/api/items/${data.id}` : "/api/items";
      let res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        alert("Save failed: " + (err.detail || res.status));
        submitBtn.disabled = false;
        return;
      }

      const saved = await res.json();

      // Upload images if present
      const files = fd.getAll("files");
      if (files.length) {
        const upfd = new FormData();
        files.forEach(f => upfd.append("files", f));
        res = await fetch(`/api/items/${saved.id}/images`, {
          method: "POST",
          body: upfd,
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          alert("Image upload failed: " + (err.detail || res.status));
        }
      }

      // Redirect to detail or list
      window.location.href = data.id
        ? `/items/${saved.id}`
        : "/items";
    }

    form.addEventListener("submit", handleSubmit);
  }

  // ————————————————
  // 2) DELETE BUTTON HANDLER
  // ————————————————
  document.querySelectorAll(".delete-btn").forEach(button => {
    button.addEventListener("click", async () => {
      if (!confirm("Are you sure you want to delete this item?")) return;
      const id = button.dataset.id;
      const res = await fetch(`/api/items/${id}`, { method: "DELETE" });
      if (res.status === 204) {
        window.location.reload();
      } else {
        const err = await res.json().catch(() => ({}));
        alert("Delete failed: " + (err.detail || res.status));
      }
    });
  });
});
