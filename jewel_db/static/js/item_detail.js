// File: jewel_db/static/js/item_detail.js

// 1️⃣ Imports
import Sortable from "https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/modular/sortable.esm.js";
import { attachTagInput } from "/static/js/tag_select.js";

// 2️⃣ Helper for safe JSON parsing
function safeParse(v) {
  try {
    return JSON.parse(v);
  } catch {
    return [];
  }
}

// 3️⃣ Wait for DOM
document.addEventListener("DOMContentLoaded", () => {
  const $ = id => document.getElementById(id);

  // ―― DOM refs ――
  const itemId = +$("item-root").dataset.itemId;
  const form = $("item-detail-form");
  const editBtn = $("edit-btn");
  const saveBtn = $("save-btn");
  const cancelBtn = $("cancel-btn");
  const delBtn = $("item-delete-btn");
  const headerName = $("header-name");
  const tagsHidden = $("tags-hidden");
  const tagsContainer = $("tags-container");
  const tagsInput = $("tags-input");
  const uploadIn = $("upload-input");
  const urlIn = $("url-input");
  const uploadBtn = $("upload-btn");
  const gallery = $("gallery");
  const lightbox = $("lightbox");
  const lbImg = $("lb-img");
  const lbPrev = $("lb-prev");
  const lbNext = $("lb-next");
  const lbClose = $("lb-close");
  const zoomInBtn = $("lb-zoom-in");
  const zoomOutBtn = $("lb-zoom-out");

  // ―― Initialize helpers ――
  attachTagInput(tagsInput, tagsHidden);
  if (window.initWebcamCapture) {
    window.initWebcamCapture("#detail-webcam-btn", "#upload-input");
  }

  // ―― Cache original values & tags ――
  const scalarEls = form.querySelectorAll("input[name], select[name], textarea[name]");
  const original = Object.fromEntries([...scalarEls].map(el => [el.name, el.value]));
  const originalTags = safeParse(tagsHidden.value);

  // ―― Tag-pill helpers ――
  function addReadonlyPill(tag) {
    const pill = document.createElement("span");
    pill.dataset.tag = tag;
    pill.className = "tag-pill-readonly text-xs bg-gray-200 px-2 py-0.5 rounded mr-1 mb-1";
    pill.textContent = tag;
    tagsContainer.appendChild(pill);
  }

  function addEditablePill(tag) {
    const pill = document.createElement("span");
    pill.dataset.tag = tag;
    pill.className = "tag-pill-editable text-xs bg-blue-600 text-white px-2 py-0.5 rounded mr-1 mb-1 cursor-pointer";
    pill.textContent = `${tag} ×`;
    pill.onclick = () => { pill.remove(); syncTags(); };
    tagsContainer.appendChild(pill);
  }

  function syncTags() {
    tagsHidden.value = JSON.stringify([...tagsContainer.children].map(el => el.dataset.tag));
  }

  tagsInput.addEventListener("tag-added", e => addEditablePill(e.detail));

  // ―― Toggle edit mode ――
  function setDisabled(state) {
    scalarEls.forEach(el => el.disabled = state);
    tagsInput.style.display = state ? "none" : "block";
  }

  // Set the form to be disabled initially
  setDisabled(true);

  // Edit button click event
  editBtn.onclick = () => {
    setDisabled(false);

    // **Replace readonly pills with editable ones**
    const readonlyPills = tagsContainer.querySelectorAll(".tag-pill-readonly");
    readonlyPills.forEach(pill => {
      const tag = pill.dataset.tag;
      pill.remove();  // Remove readonly pill
      addEditablePill(tag);  // Add editable pill
    });

    // Add editable pills for any existing tags
    originalTags.forEach(tag => addEditablePill(tag));  // Add original tags as editable pills

    tagsInput.value = "";  // Clear the tag input field
    editBtn.hidden = true;
    saveBtn.hidden = false;
    cancelBtn.hidden = false;
  };

  // Cancel button click event
  cancelBtn.onclick = () => {
    // Reset form fields to original values
    Object.entries(original).forEach(([name, val]) => {
      const el = form.querySelector(`[name="${name}"]`);
      if (el) el.value = val;
    });

    // **Re-add readonly pills and preserve original tags**
    tagsContainer.innerHTML = "";  // Clear editable pills
    (originalTags.length ? originalTags : []).forEach(addReadonlyPill);  // Add readonly pills for tags
    syncTags();

    // Set form back to read-only mode
    setDisabled(true);
    editBtn.hidden = false;
    saveBtn.hidden = true;
    cancelBtn.hidden = true;
  };

  // Save button click event
  saveBtn.onclick = async () => {
    const payload = {};
    scalarEls.forEach(el => {
      if (!el.disabled) payload[el.name] = el.value || null;
    });

    // Collect tags and add to payload
    payload.tags = [...tagsContainer.children].map(el => el.dataset.tag);

    const res = await fetch(`/api/items/${itemId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) return alert("Update failed");

    // Fetch updated item data and update UI
    const updated = await fetch(`/api/items/${itemId}`).then(r => r.json());
    Object.assign(original, updated);

    // Clear tags container and add updated tags as readonly pills
    tagsContainer.innerHTML = "";
    updated.tags.forEach(t => addReadonlyPill(t.name));
    syncTags();
    headerName.textContent = updated.name;

    // Set form back to read-only mode
    setDisabled(true);
    editBtn.hidden = false;
    saveBtn.hidden = true;
    cancelBtn.hidden = true;
  };

  // Delete item button click event
  delBtn.onclick = async () => {
    if (!confirm("Delete this item?")) return;
    if ((await fetch(`/api/items/${itemId}`, { method: "DELETE" })).ok) {
      window.location.href = "/items";
    }
  };

  // ―― Gallery / lightbox / upload ――
  let images = [];
  async function refreshGallery() {
    const data = await fetch(`/api/items/${itemId}/images`).then(r => r.json());
    images = data.map(i => i.url);
    gallery.innerHTML = data.map(i => `
      <li data-id="${i.id}" class="relative cursor-pointer border rounded overflow-hidden">
        <button data-image-id="${i.id}"
                class="image-delete-btn absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white px-1 py-0.5 rounded text-xs">×</button>
        <img src="${i.url}" class="w-full h-48 object-cover" loading="lazy"/>
        ${i.sort_order===1?`<span class="absolute top-2 left-2 bg-yellow-400 text-white px-1 rounded text-sm">★ Thumbnail</span>`:""}
      </li>
    `).join("");
  }

  new Sortable(gallery, {
    animation: 150,
    onEnd: async () => {
      const order = [...gallery.children].map(li => li.dataset.id);
      await fetch(`/api/items/${itemId}/images/reorder`, {
        method:  "PATCH",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ new_order: order }),
      });
      refreshGallery();
    },
  });

  gallery.addEventListener("click", async e => {
    if (e.target.matches(".image-delete-btn")) {
      if (!confirm("Delete this image?")) return;
      const id = e.target.dataset.imageId;
      if ((await fetch(`/api/items/${itemId}/images/${id}`, { method: "DELETE" })).ok) {
        refreshGallery();
      }
      return;
    }
    const li = e.target.closest("li");
    if (li) {
      let idx = images.indexOf(li.querySelector("img").src);
      if (idx < 0) idx = 0;
      lightbox.dataset.idx = idx;
      lbImg.src = images[idx];
      lbImg.style.transform = "scale(1)";
      lightbox.classList.remove("hidden");
    }
  });

  uploadBtn.onclick = async () => {
    const files = [...uploadIn.files];
    const url   = urlIn.value.trim();
    if (!files.length && !url) return alert("Choose files or URL");
    const fd = new FormData();
    files.forEach(f => fd.append("files", f));
    if (url) fd.append("url", url);

    uploadBtn.disabled = true;
    const ok = (await fetch(`/api/items/${itemId}/images`, { method: "POST", body: fd })).ok;
    uploadBtn.disabled = false;
    if (ok) { uploadIn.value = ""; urlIn.value = ""; refreshGallery(); }
  };

  lbClose.onclick = () => lightbox.classList.add("hidden");
  lbPrev.onclick = () => {
    let i = +lightbox.dataset.idx - 1;
    if (i < 0) i = images.length - 1;
    lightbox.dataset.idx = i;
    lbImg.src = images[i];
    lbImg.style.transform = "scale(1)";
  };
  lbNext.onclick = () => {
    let i = +lightbox.dataset.idx + 1;
    if (i >= images.length) i = 0;
    lightbox.dataset.idx = i;
    lbImg.src = images[i];
    lbImg.style.transform = "scale(1)";
  };
  const zoomLevels = [1, 1.5, 2];
  let zoomIdx = 0;
  zoomInBtn.onclick = () => {
    if (zoomIdx < zoomLevels.length - 1) zoomIdx++;
    lbImg.style.transform = `scale(${zoomLevels[zoomIdx]})`;
  };
  zoomOutBtn.onclick = () => {
    if (zoomIdx > 0) zoomIdx--;
    lbImg.style.transform = `scale(${zoomLevels[zoomIdx]})`;
  };

  // initial load
  refreshGallery();
});
