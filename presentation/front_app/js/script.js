// ─────────── Elementos DOM ───────────
const chatInput = document.getElementById("chatInput");
const resultDiv = document.getElementById("result");
const llmDropdown = document.getElementById("llmDropdown");

let currentLlm = "llm_studio";          // por defecto

// ─────────── selector de modelo ───────────
document.querySelectorAll(".dropdown-item").forEach(item => {
    item.addEventListener("click", e => {
        e.preventDefault();
        currentLlm = item.dataset.llm;
        llmDropdown.textContent = item.textContent;
    });
});

// ─────────── envío con ENTER ───────────
chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter") sendPrompt();
});

// ─────────── autocompletar desde botones de ejemplo ───────────
document.querySelectorAll(".action-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        chatInput.value = (btn.dataset.prompt || "").trim();
        chatInput.focus();
    });
});

// ─────────── llamada al backend ───────────
function sendPrompt() {
    const prompt = chatInput.value.trim();
    if (!prompt) return;

    resultDiv.innerHTML = "<em>Procesando…</em>";

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, llm_type: currentLlm })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === "success") {
            resultDiv.textContent = data.result;
        } else {
            resultDiv.textContent = `⚠️ ${data.message}`;
        }
    })
    .catch(err => {
        console.error(err);
        resultDiv.textContent = "⚠️ Error de comunicación";
    });
}
