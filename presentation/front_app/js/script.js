const chatInput   = document.getElementById('chatInput');
const resultDiv   = document.getElementById('result');
const llmDropdown = document.getElementById('llmDropdown');

let currentLlm = 'llm_studio';   // valor por defecto

document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        currentLlm = item.dataset.llm;
        llmDropdown.textContent = item.textContent;
    });
});

chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendPrompt();
});

function sendPrompt() {
    const prompt = chatInput.value.trim();
    if (!prompt) return;

    resultDiv.innerHTML = '<em>Procesando...</em>';

    fetch('/chat', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ prompt, llm_type: currentLlm })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            resultDiv.textContent = data.result;
        } else {
            resultDiv.textContent = `⚠️ ${data.message}`;
        }
    })
    .catch(err => {
        console.error(err);
        resultDiv.textContent = '⚠️ Error de comunicación';
    });
}
