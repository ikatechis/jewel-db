/* static/js/item_form.js ----------------------------------------------- */
import { attachTagInput } from "./tag_select.js";   // relative → /static/js

document.addEventListener("DOMContentLoaded", () => {
  /* ------- DOM refs ------- */
  const form       = document.getElementById("item-form");
  const fileInput  = document.getElementById("file-input");
  const urlInput   = document.getElementById("url-input");
  const tagInput   = document.getElementById("tags-input");
  const tagHidden  = document.getElementById("tags-hidden");
  const pillbox    = document.getElementById("tags-pillbox");

  /* ------- tag helper ------- */
  attachTagInput(tagInput, tagHidden);

  function addPill(tag) {
    if ([...pillbox.children].some(p => p.dataset.tag === tag)) return;
    const pill = document.createElement("span");
    pill.dataset.tag = tag;
    pill.className =
      "bg-blue-600 text-white text-xs rounded px-2 py-0.5 cursor-pointer";
    pill.textContent = `${tag} ×`;
    pill.onclick = () => { pill.remove(); syncHidden(); };
    pillbox.appendChild(pill);
    syncHidden();
  }

  function syncHidden() {
    tagHidden.value = JSON.stringify(
      [...pillbox.children]
        .map(p => p.dataset.tag)
        .filter(Boolean)          // drop empty / placeholder pills
    );
  }

  /* pre-populate pills when editing */
  try {
    JSON.parse(tagHidden.value || "[]").forEach(addPill);
  } catch (_) { /* ignore malformed JSON */ }

  /* emitted by tag_select.js when user hits Enter / comma */
  tagInput.addEventListener("tag-added", e => addPill(e.detail));

  /* optional webcam integration */
  if (typeof window.initWebcamCapture === "function") {
    window.initWebcamCapture("#webcam-btn", "#file-input");
  }

  /* ------- submit handler ------- */
  form.addEventListener("submit", async evt => {
    evt.preventDefault();
    document.querySelectorAll(".error-msg").forEach(el => (el.textContent = ""));

    const firstFile = fileInput.files[0];
    if (firstFile && !firstFile.type.startsWith("image/")) {
      fileInput.nextElementSibling.textContent = "Invalid image type";
      return;
    }

    const itemId = form.elements.id?.value;
    const isEdit = Boolean(itemId);

    const body = {
      name: form.name.value.trim(),
      category: form.category.value || null,
      material: form.material.value || null,
      gemstone: form.gemstone.value || null,
      weight:   parseFloat(form.weight.value) || 0,
      price:    parseFloat(form.price.value)  || 0,
      description: form.description.value || null,
      tags: JSON.parse(tagHidden.value || "[]"),
    };

    const url    = isEdit ? `/api/items/${itemId}` : "/api/items";
    const method = isEdit ? "PUT" : "POST";

    const r = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) { alert("Save item failed"); return; }

    const saved = await r.json();

    /* optional images or URL */
    if (fileInput.files.length || urlInput.value.trim()) {
      const fd = new FormData();
      [...fileInput.files].forEach(f => fd.append("files", f));
      const urlVal = urlInput.value.trim();
      if (urlVal) fd.append("url", urlVal);
      await fetch(`/api/items/${saved.id}/images`, { method: "POST", body: fd });
    }

    window.location.href = `/items/${saved.id}`;
  });
});
