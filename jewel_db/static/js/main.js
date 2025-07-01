// jewel_db/static/js/main.js

console.log("main.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("item-form");
  if (!form) return;

  // Grab the submit button
  const submitBtn = form.querySelector('button[type="submit"]');

  // Use a named handler so we can remove it if needed
  async function handleSubmit(e) {
    e.preventDefault();

    // Disable the button immediately to prevent duplicate clicks
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.classList.add("opacity-50", "cursor-not-allowed");
    }

    if (!form.checkValidity()) {
      form.reportValidity();
      if (submitBtn) submitBtn.disabled = false;
      return;
    }

    form.querySelectorAll(".error-msg").forEach(el => el.textContent = "");

    // 1) Gather fields
    const data = {};
    new FormData(form).forEach((v, k) => {
      if (k !== "files" && v !== "") data[k] = v;
    });

    // 2) Create or update the item
    let res = await fetch(
      data.id ? `/api/items/${data.id}` : "/api/items/",
      {
        method: data.id ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }
    );

    if (!res.ok) {
      const err = await res.json();
      if (Array.isArray(err.detail)) {
        err.detail.forEach(error => {
          const fld = form.querySelector(`[name="${error.loc[1]}"]`);
          const msg = fld?.parentElement.querySelector(".error-msg");
          if (msg) msg.textContent = error.msg;
        });
      } else {
        alert("Save failed: " + JSON.stringify(err));
      }
      if (submitBtn) submitBtn.disabled = false;
      return;
    }

    const saved = await res.json();
    const itemId = saved.id;

    // 3) Upload images exactly once
    const fileInput = form.querySelector('input[name="files"]');
    if (fileInput && fileInput.files.length) {
      console.log("Uploading", fileInput.files.length, "file(s) for item", itemId);
      const upForm = new FormData();
      for (const f of fileInput.files) upForm.append("files", f);
      const upRes = await fetch(`/api/items/${itemId}/images`, {
        method: "POST",
        body: upForm,
      });
      if (!upRes.ok) {
        const err = await upRes.json();
        alert("Image upload failed: " + (err.detail || JSON.stringify(err)));
        // We won’t re-enable the button here since we’re already redirecting
      }
      fileInput.value = "";
      console.log("Upload complete");
    }

    // 4) Redirect
    window.location.href = `/items/${itemId}`;
  }

  // Attach with { once: true } so it's removed after first invocation
  form.addEventListener("submit", handleSubmit, { once: true });
});
