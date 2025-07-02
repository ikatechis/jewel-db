/* jewel_db/static/js/webcam_capture.js
 *
 * Tiny helper to attach webcam capture to ANY
 *  <button> + <input type="file"> pair.
 *
 *  Usage (in your template scripts):
 *      initWebcamCapture('#webcam-btn', '#file-input');
 */

(() => {
  /* ------------------------------------------------------------------ */
  /*  Modal construction                                                */
  /* ------------------------------------------------------------------ */
  function buildModal() {
    const wrap = document.createElement("div");
    wrap.id = "webcam-modal";
    wrap.className =
      "fixed inset-0 z-50 hidden bg-black/60 flex items-center justify-center";
    wrap.innerHTML = `
      <div class="bg-white p-4 rounded-lg shadow-lg w-full max-w-lg">
        <!-- Video preview (un-mirrored) -->
        <video id="wc-video"
               autoplay
               playsinline
               class="w-full rounded"
               style="transform: scaleX(-1);">
        </video>

        <canvas id="wc-canvas" class="hidden"></canvas>

        <div class="mt-4 flex justify-between">
          <button id="wc-shot"
                  class="bg-blue-600 text-white px-3 py-1 rounded">
            Take&nbsp;photo
          </button>
          <button id="wc-use"
                  class="bg-green-600 text-white px-3 py-1 rounded hidden">
            Use&nbsp;photo
          </button>
          <button id="wc-close"
                  class="bg-gray-600 text-white px-3 py-1 rounded">
            Cancel
          </button>
        </div>
      </div>`;
    document.body.appendChild(wrap);
    return wrap;
  }

  /* ------------------------------------------------------------------ */
  /*  Initialiser exposed globally                                      */
  /* ------------------------------------------------------------------ */
  function init(btn, input) {
    /* btn & input can be selectors or nodes */
    const button =
      typeof btn === "string" ? document.querySelector(btn) : btn;
    const fileInput =
      typeof input === "string" ? document.querySelector(input) : input;

    if (!button || !fileInput) return;

    const modal   = buildModal();
    const video   = modal.querySelector("#wc-video");
    const canvas  = modal.querySelector("#wc-canvas");
    const shotBtn = modal.querySelector("#wc-shot");
    const useBtn  = modal.querySelector("#wc-use");
    const closeBtn = modal.querySelector("#wc-close");

    let stream;

    /* -------------------------------------------------------------- */
    /*  Utilities                                                     */
    /* -------------------------------------------------------------- */
    const stop = () => {
      stream?.getTracks().forEach((t) => t.stop());
      modal.classList.add("hidden");
      shotBtn.classList.remove("hidden");
      useBtn.classList.add("hidden");
    };

    /* -------------------------------------------------------------- */
    /*  Button handlers                                               */
    /* -------------------------------------------------------------- */
    button.addEventListener("click", async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
      } catch (err) {
        alert("Cannot access webcam: " + err.message);
        return;
      }
      video.srcObject = stream;
      modal.classList.remove("hidden");
    });

    closeBtn.onclick = stop;

    shotBtn.onclick = () => {
      canvas.width  = video.videoWidth;
      canvas.height = video.videoHeight;

      /* Draw flipped so saved file is NOT mirrored */
      const ctx = canvas.getContext("2d");
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0);

      shotBtn.classList.add("hidden");
      useBtn.classList.remove("hidden");
    };

    useBtn.onclick = () => {
      canvas.toBlob(
        (blob) => {
          const fn   = `webcam_${Date.now()}.jpg`;
          const file = new File([blob], fn, { type: "image/jpeg" });

          /* Preserve any files already picked */
          const dt = new DataTransfer();
          [...fileInput.files].forEach((f) => dt.items.add(f));
          dt.items.add(file);
          fileInput.files = dt.files;

          stop();
        },
        "image/jpeg",
        0.92
      );
    };
  }

  window.initWebcamCapture = init; // expose helper
})();
