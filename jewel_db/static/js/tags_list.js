/* tags_list.js ---------------------------------------------------------- */

/* ---------- DOM refs ---------- */
const tbody  = document.getElementById("tags-tbody");
const input  = document.getElementById("new-tag-input");
const addBtn = document.getElementById("add-tag-btn");

/* ---------- helpers ---------- */
const rowHtml = (tag) => `
  <tr data-id="${tag.id}">
    <td class="px-4 py-2">
      <span class="tag-name">${tag.name}</span>
      <input type="text"
             class="tag-edit-input border rounded p-1 w-full hidden"
             value="${tag.name}">
    </td>
    <td class="px-4 py-2 text-right space-x-2">
      <button class="edit-btn   bg-yellow-500 hover:bg-yellow-600 text-white text-xs px-2 py-0.5 rounded">Edit</button>
      <button class="save-btn   bg-green-600  hover:bg-green-700  text-white text-xs px-2 py-0.5 rounded hidden">Save</button>
      <button class="cancel-btn bg-gray-400  hover:bg-gray-500  text-white text-xs px-2 py-0.5 rounded hidden">Cancel</button>
      <button class="del-btn    bg-red-600    hover:bg-red-700   text-white text-xs px-2 py-0.5 rounded">Delete</button>
    </td>
  </tr>`;

/* ---------- load existing ---------- */
async function loadTags() {
  const tags = await fetch("/api/tags").then((r) => r.json());
  tbody.innerHTML = tags.map(rowHtml).join("");
}

/* ---------- add new ---------- */
addBtn.addEventListener("click", async () => {
  const name = input.value.trim().toLowerCase();
  if (!name) return;
  const res = await fetch("/api/tags", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (res.ok) {
    input.value = "";
    loadTags();
  } else {
    alert("Tag already exists or server error.");
  }
});

/* ---------- row actions ---------- */
tbody.addEventListener("click", async (e) => {
  const tr = e.target.closest("tr");
  if (!tr) return;

  const id        = tr.dataset.id;
  const nameSpan  = tr.querySelector(".tag-name");
  const editInput = tr.querySelector(".tag-edit-input");
  const editBtn   = tr.querySelector(".edit-btn");
  const saveBtn   = tr.querySelector(".save-btn");
  const cancelBtn = tr.querySelector(".cancel-btn");

  /* --- edit --- */
  if (e.target.classList.contains("edit-btn")) {
    nameSpan.classList.add("hidden");
    editInput.classList.remove("hidden");
    editInput.focus();
    editBtn.classList.add("hidden");
    saveBtn.classList.remove("hidden");
    cancelBtn.classList.remove("hidden");
    return;
  }

  /* --- cancel --- */
  if (e.target.classList.contains("cancel-btn")) {
    editInput.value = nameSpan.textContent;
    nameSpan.classList.remove("hidden");
    editInput.classList.add("hidden");
    saveBtn.classList.add("hidden");
    cancelBtn.classList.add("hidden");
    editBtn.classList.remove("hidden");
    return;
  }

  /* --- save --- */
  if (e.target.classList.contains("save-btn")) {
    const newName = editInput.value.trim().toLowerCase();
    if (!newName) return;
    const ok = (
      await fetch(`/api/tags/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName }),
      })
    ).ok;
    if (ok) {
      nameSpan.textContent = newName;
      nameSpan.classList.remove("hidden");
      editInput.classList.add("hidden");
      saveBtn.classList.add("hidden");
      cancelBtn.classList.add("hidden");
      editBtn.classList.remove("hidden");
    } else {
      alert("Update failed.");
    }
    return;
  }

  /* --- delete --- */
  if (e.target.classList.contains("del-btn")) {
    if (!confirm("Delete this tag?")) return;
    const ok = (await fetch(`/api/tags/${id}`, { method: "DELETE" })).ok;
    if (ok) tr.remove();
  }
});

/* ---------- init ---------- */
loadTags();
