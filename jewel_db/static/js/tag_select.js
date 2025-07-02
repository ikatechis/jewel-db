/* tag_select.js  ───────────────────────────────────────────────────────────
 *  Lightweight autocomplete for tags.
 *  • Fetches all tags once  →   const options = ["vintage", "wedding", …]
 *  • Renders a custom absolute dropdown aligned with the <input>.
 *  • Only allows selecting existing tags; free-text ignored.
 *  • Fires:
 *        tag-added   with   {detail: tagName}
 *        tag-removed with   {detail: tagName}
 *    so caller can build pills & sync hidden JSON.
 *  No external libs required.
 *  TailwindCSS used for styling.
 * ------------------------------------------------------------------------ */


export async function attachTagInput(textInput, hiddenField) {
  const allTags = await fetch("/api/tags").then(r => r.json());
  const options = allTags.map(t => t.name);
  const list    = document.createElement("div");

  list.className = [
    "tag-dd","absolute","z-50","bg-white","border","border-gray-300",
    "rounded","shadow-md","max-h-48","overflow-auto","hidden"
  ].join(" ");
  document.body.appendChild(list);

  /* ---------------- positioning ---------------- */
  function place() {
    const r = textInput.getBoundingClientRect();
    list.style.width  = r.width + "px";
    list.style.left   = r.left + window.scrollX + "px";
    list.style.top    = r.bottom + window.scrollY + "px";
  }
  window.addEventListener("resize", place);
  window.addEventListener("scroll", () => !list.classList.contains("hidden") && place());

  /* ---------------- render helpers ------------- */
  const render = arr => {
    if (!arr.length) { list.classList.add("hidden"); return; }
    list.innerHTML = arr
      .map(v => `<div data-val="${v}" class="px-3 py-1 cursor-pointer hover:bg-gray-100">${v}</div>`)
      .join("");
    place();
    list.classList.remove("hidden");
  };

  /* ---------------- show / hide ---------------- */
  const showAll  = () => render(options);
  const hideList = () => list.classList.add("hidden");

  /* open on focus or ArrowDown */
  textInput.addEventListener("focus", showAll);
  textInput.addEventListener("keydown", e => { if (e.key === "ArrowDown") showAll(); });

  /* live filter */
  textInput.addEventListener("input", () => {
    const v = textInput.value.toLowerCase();
    const m = options.filter(o => o.includes(v)).slice(0,50);
    render(v ? m : options);
  });

  /* click a suggestion */
  list.addEventListener("click", e => {
    const val = e.target.dataset.val;
    if (val) addTag(val);
  });

  /* add with Enter or comma */
  textInput.addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === ",") { e.preventDefault(); addTag(textInput.value.trim().toLowerCase()); }
    if (e.key === "Escape") hideList();
  });

  /* outside click hides list */
  document.addEventListener("click", e => {
    if (!list.contains(e.target) && e.target !== textInput) hideList();
  });

  /* ------------ add / sync ----------- */
  function addTag(tag) {
    if (!tag || !options.includes(tag)) return;
    textInput.dispatchEvent(new CustomEvent("tag-added", {detail: tag}));
    textInput.value = "";
    hideList();
  }

  /* keep hidden JSON in sync automatically */
  textInput.addEventListener("tag-added", syncHidden);
  textInput.addEventListener("tag-removed", syncHidden);
  function syncHidden() {
    const pills = [...textInput.parentNode.querySelectorAll("[data-tag]")];
    hiddenField.value = JSON.stringify(pills.map(p => p.dataset.tag));
  }
}